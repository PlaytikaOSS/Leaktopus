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
    def __init__(self, db, *args, **kwargs):
        self.db = db

    def get_status(self, scan_id: int) -> ScanStatus:
        cur = self.db.cursor()
        res = cur.execute("SELECT status FROM scans WHERE scan_id=?", (scan_id,))
        ret = res.fetchone()
        cur.close()
        if ret is None:
            raise Exception("Scan not found")
        return ScanStatus(ret["status"]).name

    def set_status(self, scan_id: int, status: ScanStatus):
        pass

    def mark_as_started(self, scan_id: int, page_number: int):
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO scan_status (scan_id, page_number, status) VALUES (?, ?, ?)",
            (scan_id, page_number, ScanStatus.SCAN_SEARCHING.name),
        )
        self.db.commit()

    def mark_as_analyzing(self, scan_id: int, page_number: int):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE scan_status SET status=? WHERE scan_id=? AND page_number=?",
            (ScanStatus.SCAN_ANALYZING.name, scan_id, page_number),
        )
        self.db.commit()

    def get_analyzing_count(self, scan_id: int) -> int:
        cur = self.db.cursor()
        res = cur.execute(
            "SELECT COUNT(*) as c FROM scan_status WHERE scan_id=? AND status=?",
            (scan_id, ScanStatus.SCAN_ANALYZING.name),
        )
        ret = res.fetchone()
        cur.close()
        return ret["c"]
