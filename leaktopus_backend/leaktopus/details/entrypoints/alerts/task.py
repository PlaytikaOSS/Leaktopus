from celery import shared_task

from leaktopus.factory import (
    create_leak_service,
    create_notification_service,
    create_alert_service,
)
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.utils.common_imports import logger


@shared_task
def send_alerts_notification_task_entrypoint():
    leak_service = create_leak_service()
    alert_service = create_alert_service()
    notification_service = create_notification_service()

    try:
        return SendAlertsNotificationTask(
            leak_service, alert_service, notification_service
        ).run()
    except NotificationException as ne:
        logger.warning("Couldn't send alerts notification. Reason: {}", ne)
    except Exception as e:
        logger.error("Error when trying to send alerts notification. Error: {}", e)
