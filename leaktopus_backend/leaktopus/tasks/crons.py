from leaktopus.utils.common_imports import logger
from leaktopus.details.entrypoints.alerts.task import (
    send_alerts_notification_task_entrypoint,
)
from celery import shared_task


@shared_task()
def cron_send_alerts_notification_task_entrypoint():
    logger.info(
        "Cron task is now running: cron_send_alerts_notification_task_entrypoint."
    )
    send_alerts_notification_task_entrypoint.s().apply_async()
