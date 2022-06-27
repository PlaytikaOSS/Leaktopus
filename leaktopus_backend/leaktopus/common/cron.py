import leaktopus.common.teams_alerter as teams
from leaktopus.app import create_celery_app

celery = create_celery_app()


@celery.task()
def cron_jobs():
    teams.alert.s().apply_async()
    return []
