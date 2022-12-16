from leaktopus.factory import create_leak_service, create_alert_service, create_notification_service
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.utils.common_imports import logger
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask


def add_leak(leak_service: LeakService):
    return leak_service.add_leak(
        "https://leakexample.com",
        "leaktopus-integration-test",
        "github",
        "",
        "",
        False,
        "2000-01-01 00:00:00"
    )


def test_send_alerts_notification_task_endpoint_with_success(
    app, client
):
    # Add leaks
    # Run task
    # Check that the alert table contains the leak
    with app.app_context():
        leak_service = create_leak_service()
        leak_id_1 = add_leak(leak_service)

        alert_service = create_alert_service()

        for notification_provider in app.config["NOTIFICATION_CONFIG"].keys():
            notification_service = create_notification_service(notification_provider)

            leaks_notified = SendAlertsNotificationTask(
                leak_service,
                alert_service,
                notification_service
            ).run()

            alert_for_leak = alert_service.get_alerts(type=notification_provider)

            sent_alert_ids = [alert.leak_id for alert in alert_for_leak]
            assert leak_id_1 in sent_alert_ids
