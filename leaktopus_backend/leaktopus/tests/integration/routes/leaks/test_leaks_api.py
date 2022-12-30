from flask import url_for
import time


def test_get_leak_by_id_with_success(
        app,
        client,
):
    with app.app_context():

        scan_response = client.get(
            url_for(
                "scans_api.start_scan",
                q="leaktopus"
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

        leak_response = client.get(
            url_for(
                "leaks_api.get_leak_by_id",
                id=1
            ),
        )

        assert leak_response.json["data"][0]["type"] == "github"
        assert len(leak_response.json["data"]) > 0
        assert len(leak_response.json["data"][0]["context"]) > 0
        assert len(leak_response.json["data"][0]["IOL"]) > 0
