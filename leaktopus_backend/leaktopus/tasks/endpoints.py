from leaktopus.app import create_celery_app
import config.settings as config
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
import os

celery = create_celery_app()


@celery.task()
def send_alerts_notification_task_endpoint():
    protocol = "https" if int(config.HTTPS_ENABLED) else "http"
    server_url = protocol + '://' + config.SERVER_NAME

    teams_token = os.environ.get('TEAMS_WEBHOOK_URL')
    if not teams_token:
        return []

    SendAlertsNotificationTask(server_url=server_url, integration_token=teams_token)\
        .run()
