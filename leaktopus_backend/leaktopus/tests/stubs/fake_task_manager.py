from leaktopus.tasks.task_manager import TaskManager


class FakeTaskManager(TaskManager):
    state = []

    def __init__(self, override_methods={}):
        self.override_methods = override_methods

    def run_tasks(self):
        return (
            self.override_methods["run_tasks"]()
            if "run_tasks" in self.override_methods
            else None
        )
