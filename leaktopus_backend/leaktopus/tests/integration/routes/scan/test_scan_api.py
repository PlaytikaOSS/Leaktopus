from flask import url_for
import time


def test_start_scan_graceful_failure_when_query_has_no_matches(
        app,
        client,
):
    with app.app_context():

        scan_response = client.get(
            url_for(
                "scans_api.start_scan",
                q="leaktopusnosuchquery"
            ),
        )

        scan_id = scan_response.json["results"][0]["scan_id"]

        scan_status = -1

        # while not scan_response.json.
        while scan_status < 3:
            scan_status_response = client.get(
                url_for(
                    "scans_api.get_scan_status",
                    id=scan_id
                ),
            )
            scan_status = scan_response.json["results"][0]["status"]
            time.sleep(2)

        assert scan_status == 3