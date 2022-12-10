from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask


def test_should_send_alerts_notification(
        factory_leak_service,
        factory_alert_service,
        factory_notification_service
):
    leak_service = factory_leak_service()
    alert_service = factory_alert_service()
    notification_service = factory_notification_service()

    leak_id = leak_service.add_leak(
        "https://leak.com",
        "leaktopus",
        "github",
        "",
        "",
        False,
        "2000-01-01 00:00:00"
    )

    SendAlertsNotificationTask(
        leak_service,
        alert_service,
        notification_service,
        server_url="https://localhost",
        integration_token="integration_token") \
        .run()

    alerts = alert_service.get_alerts()

    assert alerts[0].leak_id == leak_id
