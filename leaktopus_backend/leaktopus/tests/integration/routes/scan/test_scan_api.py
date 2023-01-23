import pytest
from flask import url_for
import time

from leaktopus.models.scan_status import ScanStatus


def start_scan(
        app_celery_db,
        client,
        **kwargs
):
    with app_celery_db.app_context():
        scan_response = client.get(
            url_for(
                "scans_api.start_scan",
                **kwargs
            ),
        )

        scan_id = scan_response.json["results"][0]["scan_id"]

        scan_status = -1

        # while scan is still in progress.
        while scan_status < ScanStatus.SCAN_DONE.value:
            scan_status_response = client.get(
                url_for(
                    "scans_api.get_scan_status",
                    id=scan_id
                ),
            )
            scan_status = scan_status_response.json["results"][0]["status"]
            time.sleep(2)

        return scan_response.json["results"][0]


def test_start_scan_ends_with_correct_scan_status_with_success(
        app_celery_db,
        client
):
    start_scan_response = start_scan(app_celery_db, client, q="Leaktopus Integration")
    scan_status = start_scan_response["status"]
    assert scan_status == ScanStatus.SCAN_DONE.value


def test_start_scan_graceful_failure_when_query_has_no_matches(
        app_celery_db,
        client
):
    start_scan_response = start_scan(app_celery_db, client, q="leaktopusnosuchquery")
    scan_status = start_scan_response["status"]
    assert scan_status == ScanStatus.SCAN_DONE.value
