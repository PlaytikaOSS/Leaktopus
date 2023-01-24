import json

import pytest
from leaktopus.factory import create_leak_service
from leaktopus.services.leak.leak import Leak


def test_should_add_leak_with_success(leak_service):
    leak_id = leak_service.add_leak("url_1", "search", "type", {}, [], False, "2021-01-01")
    assert leak_id == 5


def test_should_get_leak_context_and_iol_with_correct_types(leak_service):
    leak = leak_service.get_leaks(leak_id=1)[0]

    assert isinstance(leak.context, dict)
    assert leak.context["stargazers_count"] == 1

    assert isinstance(leak.iol, list)
    assert leak.iol[0]["file_name"] == "iol_1"


def test_should_get_leaks_with_success(leak_service):
    leaks = leak_service.get_leaks()
    assert len(leaks) == 4
    assert isinstance(leaks[0], Leak)


def test_should_get_filtered_leaks_with_success(leak_service):
    leaks = leak_service.get_leaks(url="url_1")
    assert len(leaks) == 1
    assert leaks[0].url == "url_1"

    leaks = leak_service.get_leaks(search_query="search_2")
    assert len(leaks) == 3
    assert leaks[0].search_query == "search_2"

    leaks = leak_service.get_leaks(leak_id="1")
    assert len(leaks) == 1
    assert leaks[0].leak_id == 1

    leaks = leak_service.get_leaks(type="type_2")
    assert len(leaks) == 3
    assert leaks[0].type == "type_2"

    leaks = leak_service.get_leaks(acknowledged=True)
    assert len(leaks) == 1
    assert leaks[0].acknowledged == True


def test_update_leak_with_success(leak_service):
    subject_leak_id = "1"
    leak_service.update_leak(
        subject_leak_id,
        acknowledged=True,
        context={"foo": "bar"},
    )
    leak = leak_service.get_leaks(leak_id=subject_leak_id)[0]
    assert leak.acknowledged == True
    assert leak.context["foo"] == "bar"


def test_delete_leak_by_url_with_success(leak_service):
    subject_url = "url_3"
    leak_service.delete_leak_by_url(subject_url)
    leak = leak_service.get_leaks()
    assert len(leak) == 3


def test_update_iol_append_with_success(leak_service):
    subject_leak_id = "1"
    new_iol = {
        "file_name": "iol_2",
        "file_url": "iol_2_url",
        "org_emails": ["email_3", "email_4"],
    }
    leak_service.update_iol(
        subject_leak_id,
        iol=new_iol,
    )
    leak = leak_service.get_leaks(leak_id=subject_leak_id)[0]
    assert len(leak.iol) == 2
    assert leak.iol[0]["file_name"] == "iol_1"
    assert leak.iol[0]["file_url"] == "iol_1_url"
    assert leak.iol[0]["org_emails"] == ["email_1", "email_2"]

    assert leak.iol[1]["file_name"] == "iol_2"
    assert leak.iol[1]["file_url"] == "iol_2_url"
    assert leak.iol[1]["org_emails"] == ["email_3", "email_4"]


def test_update_iol_doesnt_append_when_no_modifications(leak_service):
    subject_leak_id = "1"
    original_iol = {
        "file_name": "iol_1",
        "file_url": "iol_1_url",
        "org_emails": ["email_1", "email_2"],
    }
    leak_service.update_iol(
        subject_leak_id,
        iol=original_iol,
    )
    leak = leak_service.get_leaks(leak_id=subject_leak_id)[0]
    assert len(leak.iol) == 1
    assert leak.iol[0]["file_name"] == "iol_1"
    assert leak.iol[0]["file_url"] == "iol_1_url"
    assert leak.iol[0]["org_emails"] == ["email_1", "email_2"]

def test_update_leak_iol_overwrite_old_iol_with_success(leak_service):
    subject_leak_id = "1"
    updated_iol = [{
        "file_name": "iol_1_new",
        "file_url": "iol_1_new_url",
        "org_emails": ["email_new"],
    }]
    leak_service.update_leak(
        subject_leak_id,
        iol=updated_iol,
    )
    leak = leak_service.get_leaks(leak_id=subject_leak_id)[0]
    assert len(leak.iol) == 1
    assert leak.iol[0]["file_name"] == "iol_1_new"
    assert leak.iol[0]["file_url"] == "iol_1_new_url"
    assert leak.iol[0]["org_emails"] == ["email_new"]


@pytest.fixture()
def leak_service(app_db):
    with app_db.app_context():
        leak_service = create_leak_service()

        leak_service.add_leak("url_1", "search_1", "type_1", {
            "stargazers_count": 1,
            "forks_count": 0,
        }, [{
            "file_name": "iol_1",
            "file_url": "iol_1_url",
            "org_emails": ["email_1", "email_2"],
        }], False, "2021-01-01")
        leak_service.add_leak("url_2", "search_2", "type_2", {
            "stargazers_count": 0,
            "forks_count": 0,
        }, [{
            "file_name": "iol_2",
            "file_url": "iol_2_url",
            "org_emails": [],
        }], True, "2021-01-02")
        leak_service.add_leak("url_3", "search_2", "type_2", {
            "stargazers_count": 3,
            "forks_count": 1,
        }, [{
            "file_name": "iol_3",
            "file_url": "iol_3_url",
            "org_emails": [],
        }], False, "2021-01-02")
        leak_service.add_leak("url_4", "search_2", "type_2", {
            "stargazers_count": 1,
            "forks_count": 2,
        }, [{
            "file_name": "iol_4",
            "file_url": "iol_4_url",
            "org_emails": [],
        }], False, "2022-01-02")

        yield leak_service
