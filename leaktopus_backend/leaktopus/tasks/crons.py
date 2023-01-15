from leaktopus.utils.common_imports import logger
from leaktopus.tasks.endpoints import send_alerts_notification_task_endpoint
from leaktopus.app import create_celery_app

celery = create_celery_app()


@celery.task()
def cron_send_alerts_notification_task_endpoint():
    logger.info(
        "Cron task is now running: cron_send_alerts_notification_task_endpoint."
    )
    send_alerts_notification_task_endpoint.s().apply_async()
