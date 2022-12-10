class TaskManager:
    tasks = []

    def __init__(self, client):
        self.client = client

    def run_task(self, task, *args, **kwargs):
        self.client.run_task(task, *args, **kwargs)
        return self

    def run_tasks(self, *args, **kwargs):
        return self.client.run_tasks(*args, **kwargs)
