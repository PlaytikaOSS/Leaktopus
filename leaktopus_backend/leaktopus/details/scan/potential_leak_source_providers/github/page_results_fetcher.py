from github import RateLimitExceededException
from loguru import logger

from leaktopus.common.scanner_async import datetime_to_timestamp
from leaktopus.domain.scan.exceptions.could_not_fetch_exception import (
    CouldNotFetchException,
)
from leaktopus.domain.scan.entities.potential_leak_source import PotentialLeakSource
from leaktopus.domain.scan.contracts.potential_leak_source_page_results_fetcher_interface import (
    PotentialLeakSourcePageResultsFetcherInterface,
)


class GithubPotentialLeakSourcePageResultsFetcher(
    PotentialLeakSourcePageResultsFetcherInterface
):
    def fetch(self, results, page_num, scan_id) -> PotentialLeakSource:
        try:
            page_results = results.get_page(page_num)
            potential_leak_sources = self.generate_potential_leak_sources(page_results)
            return potential_leak_sources
            # self.fix_bug_load_page_content_before_retrieving(page_results)
            # return page_results
        except RateLimitExceededException as e:
            logger.warning(
                "Rate limit exceeded on getting page number {} from github.",
                page_num,
            )
            raise CouldNotFetchException(e)

    def generate_potential_leak_sources(self, page_results):
        potential_leak_sources = []
        for result in page_results:
            potential_leak_sources.append(self.generate_potential_leak_source(result))
            return potential_leak_sources

    def generate_potential_leak_source(self, result):
        return PotentialLeakSource(
            url=result.repository.clone_url,
            html_url=result.html_url,
            name=result.name,
            source="github",
            last_modified=datetime_to_timestamp(result.repository.last_modified),
            content=result.decoded_content.decode(),
            repo_name=result.repository.name,
            repo_description=result.repository.description,
            context={
                "repo_name": result.repository.name,
                "owner": result.repository.owner.login
                if result.repository.owner.login
                else False,
                "repo_description": result.repository.description,
                "default_branch": result.repository.default_branch,
                "is_fork": result.repository.fork,
                "forks_count": result.repository.forks_count,
                "watchers_count": result.repository.watchers_count,
                "stargazers_count": result.repository.stargazers_count,
            },
        )

    def fix_bug_load_page_content_before_retrieving(self, page_result):
        for result in page_result:
            d = result.decoded_content.decode()
