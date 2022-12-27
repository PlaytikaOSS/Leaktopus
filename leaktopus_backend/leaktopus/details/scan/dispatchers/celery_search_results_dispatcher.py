from celery import Celery, group
from loguru import logger

from leaktopus.domain.scan.contracts.search_results_dispatcher_interface import (
    SearchResultsDispatcherInterface,
)
from leaktopus.details.scan.potential_leak_source_request import (
    PotentialLeakSourceRequest,
)


class CelerySearchResultsDispatcher(SearchResultsDispatcherInterface):
    def __init__(self, client: Celery):
        self.client = client

    def dispatch(
        self,
        initial_search_metadata,
        potential_leak_source_request: PotentialLeakSourceRequest,
    ):
        from leaktopus.details.entrypoints.scan.task import (
            fetch_potential_leak_source_page_task_entrypoint,
        )

        tasks = []
        for current_page_number in range(initial_search_metadata["num_pages"]):
            tasks.append(
                fetch_potential_leak_source_page_task_entrypoint.s(
                    results=initial_search_metadata["results"],
                    number_of_pages=initial_search_metadata["num_pages"],
                    current_page_number=current_page_number,
                    potential_leak_source_request=potential_leak_source_request,
                )
            )
        logger.debug("Dispatching {} tasks", len(tasks))
        result_group = group(tasks).apply_async()
