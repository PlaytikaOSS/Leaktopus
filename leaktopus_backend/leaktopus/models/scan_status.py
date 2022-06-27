from enum import Enum


# Scan statuses definitions.
class ScanStatus(Enum):
    SCAN_SEARCHING = 1
    SCAN_ANALYZING = 2
    SCAN_INDEXING = 3
    SCAN_DONE = 4
    SCAN_FAILED = 5
    SCAN_ABORTED = 6
    SCAN_ABORTING = 7
