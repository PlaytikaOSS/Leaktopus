from abc import abstractmethod
from typing import Protocol

from leaktopus.models.scan_status import ScanStatus


class PotentialLeakSourceScanStatusProviderInterface(Protocol):
    @abstractmethod
    def get_status(self, scan_id: int) -> ScanStatus:
        pass
