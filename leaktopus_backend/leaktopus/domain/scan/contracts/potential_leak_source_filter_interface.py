from abc import abstractmethod
from typing import Protocol


class PotentialLeakSourceFilterInterface(Protocol):
    @abstractmethod
    def filter(self, scan_id, page_results):
        pass
