import os
from celery.schedules import crontab

includes = [
    'leaktopus.common.scanner_async',
    'leaktopus.common.github_indexer',
    'leaktopus.common.leak_enhancer',
    'leaktopus.tasks.crons',
    'leaktopus.tasks.endpoints'
]
max_retires = None
cronjobs = {
        "cron_send_alerts_notification_task_endpoint": {
            "task": "leaktopus.tasks.crons.send_alerts_notification_task_endpoint",
            "schedule": int(os.environ.get("CRON_INTERVAL", "60")),
        }
    }
