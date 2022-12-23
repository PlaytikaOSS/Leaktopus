from loguru import logger

from leaktopus.models.scan_status import ScanStatus
from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_provider_interface import (
    PotentialLeakSourceScanStatusProviderInterface,
)


class PotentialLeakSourceScanStatusService:
    def __init__(self, provider: PotentialLeakSourceScanStatusProviderInterface):
        self.provider = provider

    def is_aborting(self, scan_id: int) -> bool:
        logger.debug("Checking if scan is aborting")
        return self.provider.get_status(scan_id) == ScanStatus.SCAN_ABORTING
