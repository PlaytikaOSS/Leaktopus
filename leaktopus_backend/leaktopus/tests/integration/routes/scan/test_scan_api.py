from flask import url_for
import time

from leaktopus.models.scan_status import ScanStatus


def test_start_scan_ends_with_correct_scan_status_with_success(
        app_celery_db,
        client,
):
    with app_celery_db.app_context():

        scan_response = client.get(
            url_for(
                "scans_api.start_scan",
                q="Leaktopus Integration"
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
            scan_status = scan_response.json["results"][0]["status"]
            time.sleep(2)

        assert scan_status == ScanStatus.SCAN_DONE.value


def test_start_scan_graceful_failure_when_query_has_no_matches(
        app_celery_db,
        client,
):
    with app_celery_db.app_context():

        scan_response = client.get(
            url_for(
                "scans_api.start_scan",
                q="leaktopusnosuchquery"
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
            scan_status = scan_response.json["results"][0]["status"]
            time.sleep(2)

        assert scan_status == ScanStatus.SCAN_DONE.value
