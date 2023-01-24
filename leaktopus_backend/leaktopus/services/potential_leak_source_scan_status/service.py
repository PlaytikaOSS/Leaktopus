from loguru import logger

from leaktopus.models.scan_status import ScanStatus
from leaktopus.services.potential_leak_source_scan_status.interface import (
    PotentialLeakSourceScanStatusProviderInterface,
)


class PotentialLeakSourceScanStatusService:
    def __init__(self, provider: PotentialLeakSourceScanStatusProviderInterface):
        self.provider = provider

    def is_aborting(self, scan_id: int) -> bool:
        return self.provider.get_status(scan_id) == ScanStatus.SCAN_ABORTING

    def set_status(self, scan_id: int, status: ScanStatus):
        self.provider.set_status(scan_id, status)

    def get_status(self, scan_id: int) -> ScanStatus:
        return self.provider.get_status(scan_id)

    def mark_as_started(self, scan_id: int, page_number: int):
        self.provider.mark_as_started(scan_id, page_number)

    def mark_as_analyzing(self, scan_id: int, page_number: int):
        self.provider.mark_as_analyzing(scan_id, page_number)

    def get_analyzing_count(self, scan_id: int) -> int:
        return self.provider.get_analyzing_count(scan_id)
