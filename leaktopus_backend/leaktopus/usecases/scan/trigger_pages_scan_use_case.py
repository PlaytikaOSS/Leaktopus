from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.tasks.potential_leak_source_request import PotentialLeakSourceRequest
from leaktopus.usecases.scan.search_results_dispatcher_interface import (
    SearchResultsDispatcherInterface,
)


class CollectPotentialLeakSourcePagesUseCase:
    def __init__(
        self,
        potential_leak_source_scan_status_service: PotentialLeakSourceScanStatusService,
        search_results_dispatcher: SearchResultsDispatcherInterface,
    ):
        self.potential_leak_source_scan_status_service = (
            potential_leak_source_scan_status_service
        )
        self.search_results_dispatcher = search_results_dispatcher

    def execute(
        self,
        initial_search_metadata,
        potential_leak_source_request: PotentialLeakSourceRequest,
    ):
        self.guard_initial_search_metadata(initial_search_metadata)
        self.guard_scan_is_aborting(potential_leak_source_request.scan_id)
        self.search_results_dispatcher.dispatch(
            initial_search_metadata, potential_leak_source_request
        )

    def guard_initial_search_metadata(self, initial_search_metadata):
        if not initial_search_metadata:
            raise Exception("initial_search_metadata is empty")

        if (
            not initial_search_metadata["results"]
            # or len(initial_search_metadata["results"]) == 0 TypeError: object of type 'PaginatedList' has no len()
        ):
            raise Exception("initial_search_metadata.results is empty")

        if (
            not initial_search_metadata["num_pages"]
            # or initial_search_metadata["num_pages"] == 0 TypeError: object of type 'PaginatedList' has no len()
        ):
            raise Exception("initial_search_metadata.num_pages is empty")

    def guard_scan_is_aborting(self, scan_id):
        if self.potential_leak_source_scan_status_service.is_aborting(scan_id):
            raise Exception("Scan is aborting")
