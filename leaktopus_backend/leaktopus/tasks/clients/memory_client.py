class MemoryClient:
    executed_tasks = []

    def __init__(self, override_tasks={}):
        self.override_tasks = override_tasks

    def run_task(self, task, *args, **kwargs):
        if "run_task" in self.override_tasks:
            self.override_tasks["run_task"]()
        else:
            self.executed_tasks.append(task.name)

    def run_tasks(self, *args, **kwargs):
        for task in self.tasks:
            task.run(args, kwargs)
