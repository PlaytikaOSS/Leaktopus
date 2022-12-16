from flask import url_for


def test_integration_should_send_ms_teams_test_notification_with_success(app, client):
    with app.app_context():
        response = client.get(
            url_for(
                "alerts_api.notification_test",
                integration_type='ms_teams'
            ),
        )

    assert 200 == response.status_code


def test_integration_should_send_slack_test_notification_with_success(app, client):
    with app.app_context():
        response = client.get(
            url_for(
                "alerts_api.notification_test",
                integration_type='slack'
            ),
        )

    assert 200 == response.status_code
