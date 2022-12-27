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


class PastebinPotentialLeakSourcePageResultsFetcher(
    PotentialLeakSourcePageResultsFetcherInterface
):
    def fetch(self, results, page_num, scan_id) -> PotentialLeakSource:
        raise NotImplementedError
