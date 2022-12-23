from github import RateLimitExceededException
from loguru import logger

from leaktopus.usecases.scan.could_not_fetch_exception import CouldNotFetchException
from leaktopus.usecases.scan.potential_leak_source_page_results_fetcher_interface import (
    PotentialLeakSourcePageResultsFetcherInterface,
)


class GithubPotentialLeakSourcePageResultsFetcher(
    PotentialLeakSourcePageResultsFetcherInterface
):
    def fetch(self, results, page_num, scan_id):
        try:
            page_result = results.get_page(page_num)
            self.fix_bug_load_page_content_before_retrieving(page_result)
            return page_result
        except RateLimitExceededException as e:
            logger.warning(
                "Rate limit exceeded on getting page number {} from github.",
                page_num,
            )
            raise CouldNotFetchException(e)

    def fix_bug_load_page_content_before_retrieving(self, page_result):
        for result in page_result:
            d = result.decoded_content.decode()
            # d = result.last_modified
            # logger.debug("Decoded content: {}", d)
