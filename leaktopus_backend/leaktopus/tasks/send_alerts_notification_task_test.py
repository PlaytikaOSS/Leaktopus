from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask


def test_should_send_alerts_notification(
        add_leak,
        factory_leak_service,
        factory_alert_service,
        factory_notification_service
):
    leak_service = factory_leak_service()
    alert_service = factory_alert_service()
    notification_service = factory_notification_service()

    leak_id_1 = add_leak(leak_service)

    notified_leaks_1 = SendAlertsNotificationTask(
        leak_service,
        alert_service,
        notification_service).run()

    # One leaks should have been handled.
    assert len(notified_leaks_1) == 1

    # Verify that alerts were saved to storage.
    alerts = alert_service.get_alerts()
    assert alerts[0].leak_id == leak_id_1

    # Now add another leak and see that it only sends this leak in the notification.
    leak_id_2 = add_leak(leak_service)

    notified_leaks_2 = SendAlertsNotificationTask(
        leak_service,
        alert_service,
        notification_service).run()
    assert len(notified_leaks_2) == 1

    # Now check that no notifications will be sent if no new leaks.
    notified_leaks_3 = SendAlertsNotificationTask(
        leak_service,
        alert_service,
        notification_service).run()
    assert len(notified_leaks_3) == 0


def test_should_not_send_alerts_notification_when_no_leaks(
        factory_leak_service,
        factory_alert_service,
        factory_notification_service
):
    leak_service = factory_leak_service()
    alert_service = factory_alert_service()
    notification_service = factory_notification_service()

    notified_leaks_1 = SendAlertsNotificationTask(
        leak_service,
        alert_service,
        notification_service).run()
    assert len(notified_leaks_1) == 0


def test_should_send_multiple_leaks_in_notification(
        add_leak,
        factory_leak_service,
        factory_alert_service,
        factory_notification_service
):
    leak_service = factory_leak_service()
    alert_service = factory_alert_service()
    notification_service = factory_notification_service()

    leak_id_1 = add_leak(leak_service)
    leak_id_2 = add_leak(leak_service)
    leak_id_3 = add_leak(leak_service)

    notified_leaks_1 = SendAlertsNotificationTask(
        leak_service,
        alert_service,
        notification_service).run()

    # One leaks should have been handled.
    assert len(notified_leaks_1) == 3

    # Verify that alerts were saved to storage.
    alerts = alert_service.get_alerts()
    assert alerts[0].leak_id == leak_id_1
    assert alerts[1].leak_id == leak_id_2
    assert alerts[2].leak_id == leak_id_3
