from leaktopus.app import create_celery_app
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.factory import create_leak_service, create_notification_service, create_alert_service

celery = create_celery_app()


@celery.task()
def send_alerts_notification_task_endpoint():
    leak_service = create_leak_service()
    alert_service = create_alert_service()
    notification_service = create_notification_service()

    return SendAlertsNotificationTask(
        leak_service,
        alert_service,
        notification_service
    ).run()
