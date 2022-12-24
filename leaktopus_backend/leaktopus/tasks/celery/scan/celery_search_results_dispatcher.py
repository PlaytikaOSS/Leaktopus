from celery import Celery, group
from loguru import logger

from leaktopus.usecases.scan.search_results_dispatcher_interface import (
    SearchResultsDispatcherInterface,
)


class CelerySearchResultsDispatcher(SearchResultsDispatcherInterface):
    def __init__(self, client: Celery):
        self.client = client

    def dispatch(self, initial_search_metadata, scan_id, organization_domains):
        from leaktopus.tasks.endpoints import (
            fetch_potential_leak_source_page_task_endpoint,
        )

        tasks = []
        for page_num in range(initial_search_metadata["num_pages"]):
            tasks.append(
                fetch_potential_leak_source_page_task_endpoint.s(
                    results=initial_search_metadata["results"],
                    page_num=page_num,
                    scan_id=scan_id,
                    search_query=initial_search_metadata["search_query"],
                    organization_domains=organization_domains,
                )
            )
        logger.debug("Dispatching {} tasks", len(tasks))
        result_group = group(tasks).apply_async()
