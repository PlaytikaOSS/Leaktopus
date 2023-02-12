from leaktopus.utils.common_imports import logger
from leaktopus.domain.scan.contracts.search_results_dispatcher_interface import (
    SearchResultsDispatcherInterface,
)
from leaktopus.details.scan.potential_leak_source_request import (
    PotentialLeakSourceRequest,
)


class CelerySearchResultsDispatcher(SearchResultsDispatcherInterface):

    def dispatch(
        self,
        initial_search_metadata,
        potential_leak_source_request: PotentialLeakSourceRequest,
    ):
        from leaktopus.details.entrypoints.scan.task import (
            fetch_potential_leak_source_page_task_entrypoint,
        )

        logger.debug("Dispatching {} tasks", initial_search_metadata["num_pages"])

        for current_page_number in range(initial_search_metadata["num_pages"]):
            fetch_potential_leak_source_page_task_entrypoint.s(
                results=initial_search_metadata["results"],
                number_of_pages=initial_search_metadata["num_pages"],
                current_page_number=current_page_number,
                potential_leak_source_request=potential_leak_source_request,
            ).apply_async()
