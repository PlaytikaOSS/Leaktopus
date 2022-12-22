from abc import abstractmethod
from typing import Protocol

from leaktopus.common.db_handler import get_db
from leaktopus.models.scan_status import ScanStatus
from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_provider_interface import (
    PotentialLeakSourceScanStatusProviderInterface,
)


class SqlitePotentialLeakSourceScanStatusProvider(
    PotentialLeakSourceScanStatusProviderInterface
):
    def __init__(self):
        pass
        # self.db = get_db()

    def get_status(self, scan_id: int) -> ScanStatus:
        pass
