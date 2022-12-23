from abc import abstractmethod
from typing import Protocol


class PotentialLeakSourcePageResultsSaverInterface(Protocol):
    @abstractmethod
    def save(self, page_results, scan_id):
        pass
