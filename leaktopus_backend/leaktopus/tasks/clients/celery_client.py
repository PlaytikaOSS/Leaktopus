from celery import group
from celery.result import allow_join_result

from leaktopus.utils.common_imports import logger


class CeleryClient:
    def __init__(self):
        self.tasks = {}
        self.tasks_to_run = []

    def run_task(self, task, *args, **kwargs):
        logger.debug(f"Adding task {task} : {args} : {kwargs}")
        task.apply_async()

    def run_tasks(self):
        task_group = group(self.tasks_to_run)
        result_group = task_group.apply_async()
        # Waiting for all scan execution tasks to finish.
        while result_group.waiting():
            continue

        with allow_join_result():
            for task in self.tasks_to_run:
                task.run_after(result_group)
