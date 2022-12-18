from leaktopus.app import create_celery_app
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.factory import create_leak_service, create_notification_service, create_alert_service
from leaktopus.utils.common_imports import logger

celery = create_celery_app()


@celery.task()
def send_alerts_notification_task_endpoint():
    leak_service = create_leak_service()
    alert_service = create_alert_service()
    notification_service = create_notification_service()

    try:
        return SendAlertsNotificationTask(
            leak_service,
            alert_service,
            notification_service
        ).run()
    except NotificationException as ne:
        logger.warning("Couldn't send alerts notification. Reason: {}", ne)
    except Exception as e:
        logger.errpr("Error when trying to send alerts notification. Error: {}", e)
