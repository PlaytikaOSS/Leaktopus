import json
import re
from abc import abstractmethod

import pytest
from loguru import logger

from leaktopus.common.scanner_async import datetime_to_timestamp
from leaktopus.services.ignore_pattern.ignore_pattern_provider_interface import (
    IgnorePatternProviderInterface,
)
from leaktopus.services.ignore_pattern.ignore_pattern_service import (
    IgnorePatternService,
)
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.provider_interface import LeakProviderInterface
from leaktopus.usecases.scan.domain_extractor import DomainExtractor
from leaktopus.usecases.scan.email_extractor import EmailExtractor
from leaktopus.usecases.scan.potential_leak_source_filter_interface import (
    PotentialLeakSourceFilterInterface,
)


class PotentialLeakSourceFilter(PotentialLeakSourceFilterInterface):
    def __init__(
        self,
        leak_service: LeakService,
        ignore_pattern_service: IgnorePatternService,
        domain_extractor: DomainExtractor,
        email_extractor: EmailExtractor,
        max_domain_emails: int,
        max_non_org_emails: int,
        max_fork_count: int,
        max_star_count: int,
    ):
        self.leak_service = leak_service
        self.ignore_pattern_service = ignore_pattern_service
        self.domain_extractor = domain_extractor
        self.email_extractor = email_extractor
        self.max_domain_emails = max_domain_emails
        self.max_non_org_emails = max_non_org_emails
        self.max_fork_count = max_fork_count
        self.max_star_count = max_star_count

    def filter(self, scan_id, result):
        if self.is_ignored_repo(result):
            return False

        if not self.is_repo_requires_scan(result):
            return False

        if self.fork_count_is_too_high(result):
            return False

        if self.star_count_is_too_high(result):
            return False

        content = self.fetch_file_content(result)
        if self.too_many_non_org_emails(content):
            return False

        if self.too_many_domain_emails(content):
            return False

        return True

    def is_ignored_repo(self, repo_url):
        ignored_patterns = self.ignore_pattern_service.get_ignore_patterns()
        if not ignored_patterns:
            return False

        for pattern in ignored_patterns:
            if re.search(rf"{pattern['pattern']}", repo_url):
                return True

        return False

    def is_repo_requires_scan(self, repo):
        leaks = self.leak_service.get_leaks(url=self.extract_url_from_repo(repo))
        if self.leak_not_scanned(leaks):
            return True

        if self.repository_was_updated_since_last_scan(repo, leaks):
            return True

        return False

    @abstractmethod
    def extract_url_from_repo(self, repo):
        raise NotImplementedError

    def leak_not_scanned(self, leaks):
        return not leaks

    def repository_was_updated_since_last_scan(self, repo, leaks):
        known_last_modified = leaks["last_modified"]
        last_modified = datetime_to_timestamp(self.extract_last_modified(repo))
        if last_modified > known_last_modified:
            return True

    @abstractmethod
    def extract_last_modified(self, repo):
        raise NotImplementedError

    @abstractmethod
    def extract_star_count(self, repo):
        raise NotImplementedError

    @abstractmethod
    def extract_fork_count(self, repo):
        raise NotImplementedError

    def fork_count_is_too_high(self, repo):
        return self.extract_fork_count(repo) >= self.max_fork_count

    def star_count_is_too_high(self, repo):
        return self.extract_star_count(repo) >= self.max_star_count

    def too_many_non_org_emails(self, content):
        emails = self.email_extractor.extract_non_organization_emails(content)
        return len(emails) >= self.max_non_org_emails

    def too_many_domain_emails(self, content):
        domains = self.domain_extractor.extract(content)
        return len(domains) >= self.max_domain_emails

    @abstractmethod
    def fetch_file_content(self, result):
        raise NotImplementedError


class GithubPotentialLeakSourceFilter(PotentialLeakSourceFilter):
    def fetch_file_content(self, result):
        try:
            return result.decoded_content.decode()
        except AssertionError as e:
            logger.warning("Couldn't decode content for result: {}", e)

    def extract_last_modified(self, repo):
        return repo.repository.last_modified

    def extract_url_from_repo(self, repo):
        return repo.repository.clone_url

    def extract_star_count(self, repo):
        if repo.repository.stargazers_count is None:
            return 0
        return int(repo.repository.stargazers_count)

    def extract_fork_count(self, repo):
        if repo.repository.forks_count is None:
            return 0
        return int(repo.repository.forks_count)


def test_github_potential_leak_source_filter(
    leak_provider_mock, ignore_pattern_provider_mock
):
    result = PaginatedList()
    filter = GithubPotentialLeakSourceFilter(
        leak_service=LeakService(leak_provider=leak_provider_mock),
        ignore_pattern_service=IgnorePatternService(ignore_pattern_provider_mock),
        domain_extractor=DomainExtractor(),
        email_extractor=EmailExtractor(
            organization_domains=["example.com", "example.org"]
        ),
        max_domain_emails=10,
        max_non_org_emails=10,
        min_star_count=0,
        max_star_count=1000,
    )
    filter.filter(1, result)


class SavePotentialLeakSourcePageUseCase:
    def __init__(
        self,
        leak_service: LeakService,
        potential_leak_source_filter: PotentialLeakSourceFilterInterface,
        email_extractor: EmailExtractor,
    ):
        self.leak_service = leak_service
        self.potential_leak_source_filter = potential_leak_source_filter
        self.email_extractor = email_extractor

    def execute(self, scan_id, page_results, search_query):
        self.guard_empty_page_results(page_results)
        logger.info("Saving page results for scan id: {}", scan_id)
        logger.info("Page results: {}", page_results)
        filtered_results = self.filter_results(scan_id, page_results)
        grouped_results = self.group_results_before_save(filtered_results, search_query)
        self.save_results(grouped_results, search_query)

    def save_results(self, grouped_results, search_query):
        for leaks_repo in grouped_results:
            existing_leak = self.leak_service.get_leaks(url=leaks_repo["url"])
            # @todo Update leak in case that the repo was modified since previous scan and it wasn't acknowledged yet.
            if existing_leak and not existing_leak["acknowledged"]:
                continue

            self.leak_service.add_leak(
                leaks_repo["url"],
                search_query,
                "github",
                json.dumps(leaks_repo["context"]),
                json.dumps(leaks_repo["leaks"]),
                False,
                leaks_repo["last_modified"],
            )

    def group_results_before_save(self, filtered_results, search_query):
        grouped_results = []
        for result in filtered_results:
            org_emails = self.email_extractor.extract_organization_emails(
                json.dumps(result.decoded_content.decode())
            )
            leak_data = self.generate_leak_data(result, org_emails)
            is_url_exists = self.is_url_exists(grouped_results, result)
            self.append_or_update_group_result(
                grouped_results, is_url_exists, leak_data, search_query, result
            )
        return grouped_results

    def guard_empty_page_results(self, page_results):
        if not page_results:
            raise ValueError("Page results cannot be empty")

    def filter_results(self, scan_id, page_results):
        filtered_results = []
        for result in page_results:
            if self.potential_leak_source_filter.filter(scan_id, result):
                filtered_results.append(result)
        return filtered_results

    def generate_leak_data(self, search_result, org_emails):
        return {
            "file_name": search_result.name,
            "file_url": search_result.html_url,
            "org_emails": org_emails,
        }

    def is_url_exists(self, grouped_results, search_result):
        is_url_exists = False
        for gr in grouped_results:
            if gr["url"] == search_result.repository.clone_url:
                is_url_exists = True
                break
        return is_url_exists

    def append_or_update_group_result(
        self, grouped_results, is_url_exists, leak_data, search_query, search_result
    ):
        if is_url_exists:
            existing_res_key = None
            for i, gr in enumerate(grouped_results):
                if gr["url"] == search_result.repository.clone_url:
                    existing_res_key = i

            grouped_results[existing_res_key]["leaks"].append(leak_data)
        else:
            grouped_results.append(
                self.generate_result(
                    grouped_results, search_result, search_query, leak_data
                )
            )

    def generate_result(self, grouped_results, search_result, search_query, leak_data):
        return {
            "url": search_result.repository.clone_url,
            "last_modified": datetime_to_timestamp(search_result.last_modified),
            "leaks": [leak_data],
            "search_query": search_query,
            "type": "github",
            "context": {
                "repo_name": search_result.repository.name,
                "owner": search_result.repository.owner.login
                if search_result.repository.owner.login
                else False,
                "repo_description": search_result.repository.description,
                "default_branch": search_result.repository.default_branch,
                "is_fork": search_result.repository.fork,
                "forks_count": search_result.repository.forks_count,
                "watchers_count": search_result.repository.watchers_count,
                "stargazers_count": search_result.repository.stargazers_count,
            },
        }


def test_should_save_potential_leak_source_page_successfully(
    leak_provider_mock,
    ignore_pattern_provider_mock,
    potential_leak_source_filter_mock,
    page_results,
):
    search_query = "test"
    scan_id = 1

    leak_provider_mock.add_leak.return_value = None
    ignore_pattern_provider_mock.get_ignore_patterns.return_value = []
    potential_leak_source_filter_mock.filter.return_value = True

    leak_service = LeakService(leak_provider=leak_provider_mock)
    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter_mock,
        email_extractor=EmailExtractor(organization_domains=["test.com", "test2.com"]),
    )
    use_case.execute(scan_id, page_results, search_query)
    leak_provider_mock.add_leak.assert_called()


@pytest.fixture
def leak_provider_mock(mocker):
    return mocker.patch.object(LeakProviderInterface, "add_leak")


@pytest.fixture
def potential_leak_source_filter_mock(mocker):
    return mocker.patch.object(PotentialLeakSourceFilterInterface, "filter")


@pytest.fixture
def ignore_pattern_provider_mock(mocker):
    return mocker.patch.object(IgnorePatternProviderInterface, "get_ignore_patterns")


@pytest.fixture
def page_results():
    return [
        {
            "name": "test.txt",
            "html_url": "asdasdf",
            "clone_url": "aasd1",
            "repository": {
                "name": "test",
                "owner": {"login": "test"},
                "description": "test",
                "default_branch": "master",
                "fork": False,
                "forks_count": 0,
                "watchers_count": 0,
                "stargazers_count": 0,
                "last_modified": "Sat, 19 Dec 2022 15:34:56 UTC",
            },
        },
        {
            "name": "test.txt",
            "html_url": "asdasdf",
            "clone_url": "aasd2",
            "repository": {
                "name": "test",
                "owner": {"login": "test"},
                "description": "test",
                "default_branch": "master",
                "fork": False,
                "forks_count": 0,
                "watchers_count": 0,
                "stargazers_count": 0,
                "last_modified": "Sat, 19 Dec 2022 15:34:56 UTC",
            },
        },
        {
            "name": "test.txt",
            "html_url": "asdasdf",
            "clone_url": "aasd1",
            "repository": {
                "name": "test",
                "owner": {"login": "test"},
                "description": "test",
                "default_branch": "master",
                "fork": False,
                "forks_count": 0,
                "watchers_count": 0,
                "stargazers_count": 0,
                "last_modified": "Sat, 19 Dec 2022 15:34:56 UTC",
            },
        },
    ]
