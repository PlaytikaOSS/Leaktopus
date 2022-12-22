from celery import Celery

from leaktopus.usecases.scan.potential_leak_source_page_results_saver_interface import (
    PotentialLeakSourcePageResultsSaverInterface,
)


class CeleryPotentialLeakSourcePageResultsSaver(
    PotentialLeakSourcePageResultsSaverInterface
):
    def __init__(self, client: Celery):
        self.client = client

    def save(self, page_results, scan_id):
        from leaktopus.tasks.endpoints import (
            save_potential_leak_source_page_results_task_endpoint,
        )

        save_potential_leak_source_page_results_task_endpoint.s(
            page_results=page_results, scan_id=scan_id
        ).apply_async()
