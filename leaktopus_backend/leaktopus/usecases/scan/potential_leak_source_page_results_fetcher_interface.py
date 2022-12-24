from abc import abstractmethod
from typing import Protocol

from leaktopus.usecases.scan.potential_leak_source import PotentialLeakSource


class PotentialLeakSourcePageResultsFetcherInterface(Protocol):
    @abstractmethod
    def fetch(self, results, page_num, scan_id) -> PotentialLeakSource:
        pass
