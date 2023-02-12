from github import RateLimitExceededException
from leaktopus.utils.common_imports import logger
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

    def generate_potential_leak_source(self, result) -> PotentialLeakSource:
        repo = result.repository
        content = result.decoded_content.decode()
        return PotentialLeakSource(
            url=repo.clone_url,
            html_url=result.html_url,
            name=result.name,
            source="github",
            last_modified=datetime_to_timestamp(repo.last_modified),
            content=content,
            context={
                "repo_name": repo.name,
                "owner": repo.owner.login
                if repo.owner.login
                else False,
                "repo_description": repo.description,
                "default_branch": repo.default_branch,
                "is_fork": repo.fork,
                "forks_count": repo.forks_count,
                "watchers_count": repo.watchers_count,
                "stargazers_count": repo.stargazers_count,
            },
        )
