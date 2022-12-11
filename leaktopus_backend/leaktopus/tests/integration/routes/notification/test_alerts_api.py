from flask import url_for


def test_integration_should_send_ms_teams_test_notification_with_success(app, client):
    with app.app_context():
        response = client.get(
            url_for("alerts_api.teams_webhook_test"),
        )

    assert 200 == response.status_code
