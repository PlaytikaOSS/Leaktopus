import json

import pytest
from flask import url_for
import time

from leaktopus.models.scan_status import ScanStatus


def get_leak_by_id(
        app_celery_db,
        client,
        leak_id
):
    with app_celery_db.app_context():
        leaks_response = client.get(
            url_for(
                "leaks_api.get_leak_by_id",
                id=leak_id
            ),
        )
    return leaks_response.json["data"][0]


def start_scan(
        app_celery_db,
        client,
        extended_scan,
        **kwargs
):
    with app_celery_db.app_context():
        if extended_scan:
            scan_response = client.post(
                url_for(
                    "scans_api.start_scan_extended",
                ),
                json=kwargs
            )
        else:
            scan_response = client.get(
                url_for(
                    "scans_api.start_scan",
                    **kwargs
                )
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


def assert_leak_has_base_data(leak):
    assert len(leak) > 0
    assert leak["type"] == "github"
    assert len(leak["context"]) > 0
    assert len(leak["iol"]) > 0


def test_scan_ends_with_correct_scan_status_with_success(
        app_celery_db,
        client
):
    start_scan_response = start_scan(app_celery_db, client, False, q="Leaktopus Integration")
    scan_status = start_scan_response["status"]
    assert scan_status == ScanStatus.SCAN_DONE.value


def test_scan_ends_with_saved_leaks_with_success(
        app_celery_db,
        client
):
    start_scan(app_celery_db, client, False, q="Leaktopus Integration")
    leak = get_leak_by_id(app_celery_db, client, 1)

    assert_leak_has_base_data(leak)


def test_scan_extended_ends_with_correct_scan_status_with_success(
        app_celery_db,
        client
):
    sensitive_keyword = "a20958f0-e141-4804-8ab8-e37b90620ae5"
    domain = "github.com"
    start_scan_response = start_scan(
        app_celery_db, client, True,
        q="Leaktopus Integration",
        enhancement_modules=["domains", "sensitive_keywords", "contributors", "secrets"],
        organization_domains=domain,
        sensitive_keywords=[sensitive_keyword]
    )
    scan_status = start_scan_response["status"]
    assert scan_status == ScanStatus.SCAN_DONE.value

    leak = get_leak_by_id(app_celery_db, client, 1)
    assert_leak_has_base_data(leak)

    from loguru import logger
    logger.debug(leak)
    assert sensitive_keyword in leak["sensitive_keywords"][0]["keyword"]
    assert domain in leak["domains"][0]["domain"]

    contributors = leak["contributors"]
    assert "noreply@github.com" in contributors[0]["committer_email"]
    assert contributors[0]["is_organization_domain"] == 1

    assert "AKIAIOSFODNN7EXAMPAA" in leak["secrets"][0]["match_string"]


def test_scan_graceful_failure_when_search_has_no_results(
        app_celery_db,
        client
):
    start_scan_response = start_scan(app_celery_db, client, False, q="leaktopusnosuchquery")
    scan_status = start_scan_response["status"]
    assert scan_status == ScanStatus.SCAN_DONE.value
