from github import RateLimitExceededException
from loguru import logger

from leaktopus.usecases.scan.could_not_fetch_exception import CouldNotFetchException
from leaktopus.usecases.scan.potential_leak_source_page_results_fetcher_interface import (
    PotentialLeakSourcePageResultsFetcherInterface,
)


class CeleryPotentialLeakSourcePageResultsFetcher(
    PotentialLeakSourcePageResultsFetcherInterface
):
    def fetch(self, results, page_num, scan_id):
        try:
            return results.get_page(page_num)
        except RateLimitExceededException as e:
            logger.warning(
                "Rate limit exceeded on getting page number {} from github.",
                page_num,
            )
            raise CouldNotFetchException(e)
