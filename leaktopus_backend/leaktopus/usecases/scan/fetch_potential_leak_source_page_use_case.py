from loguru import logger

from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.usecases.scan.potential_leak_source_page_results_fetcher_interface import (
    PotentialLeakSourcePageResultsFetcherInterface,
)


class FetchPotentialLeakSourcePageUseCase:
    def __init__(
        self,
        potential_leak_source_scan_status_service: PotentialLeakSourceScanStatusService,
        potential_leak_source_page_results_fetcher: PotentialLeakSourcePageResultsFetcherInterface,
    ):
        self.potential_leak_source_scan_status_service = (
            potential_leak_source_scan_status_service
        )
        self.potential_leak_source_page_results_fetcher = (
            potential_leak_source_page_results_fetcher
        )

    def execute(self, results, page_num, scan_id):
        self.guard_scan_is_aborting(scan_id)
        page_results = self.potential_leak_source_page_results_fetcher.fetch(
            results, page_num, scan_id
        )
        return page_results

    def guard_scan_is_aborting(self, scan_id):
        if self.potential_leak_source_scan_status_service.is_aborting(scan_id):
            raise Exception("Scan is aborting")
