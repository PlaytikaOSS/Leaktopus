from abc import abstractmethod
from typing import Protocol

from leaktopus.models.scan_status import ScanStatus


class PotentialLeakSourceScanStatusProviderInterface(Protocol):
    @abstractmethod
    def get_status(self, scan_id: int) -> ScanStatus:
        pass

    @abstractmethod
    def set_status(self, scan_id: int, status: ScanStatus):
        pass

    def mark_as_started(self, scan_id: int, page_number: int):
        pass

    def mark_as_analyzing(self, scan_id: int, page_number: int):
        pass

    def get_analyzing_count(self, scan_id: int) -> int:
        pass
