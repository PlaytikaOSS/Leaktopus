from celery import shared_task
from flask import current_app

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

    for notification_provider in current_app.config["NOTIFICATION_CONFIG"].keys():
        try:
            notification_service = create_notification_service(notification_provider)
            return SendAlertsNotificationTask(
                leak_service, alert_service, notification_service
            ).run()

        except NotificationException as e:
            logger.warning(
                "Cannot send alerts notification via send_notifications route. Message: {}",
                e,
            )
        except Exception as e:
            logger.error(
                "Error sending alerts notification via send_notifications route. Message: {}",
                e,
            )
