import uuid

from typing import Protocol


class Task(Protocol):
    task_id = uuid.uuid1()

    def id(self):
        return self.task_id
