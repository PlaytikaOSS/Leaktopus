from abc import abstractmethod
from typing import Protocol


class PotentialLeakSourcePageResultsFetcherInterface(Protocol):
    @abstractmethod
    def fetch(self, results, page_num, scan_id):
        pass
