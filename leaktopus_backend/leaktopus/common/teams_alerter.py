import leaktopus.utils.alerts as alerts
import config.settings as config
import pymsteams
import os
from leaktopus.app import create_celery_app

celery = create_celery_app()


@celery.task()
def alert():
    teams_token = os.environ.get('TEAMS_WEBHOOK_URL')
    if not teams_token:
        return []

    protocol = "https" if int(config.HTTPS_ENABLED) else "http"
    new_leaks = alerts.get_leaks_to_alert(alerts.TEAMS)
    for leak in new_leaks:
        message = pymsteams.connectorcard(teams_token)
        message.title("A new leak has been found by Leaktopus")
        message.text(f"A new leak has been found for the search query: {leak['search_query']}")
        message.addLinkButton("Click here to view leak ", f"{protocol}://{config.SERVER_NAME}/api/leak/{leak['pid']}")
        message.send()
        alerts.add_alert(leak["pid"], alerts.TEAMS)
    return f"Sent {len(new_leaks)} new alerts"


def test_teams_webhook():
    teams_token = os.environ.get('TEAMS_WEBHOOK_URL')
    if not teams_token:
        return "Error: Teams webhook is missing."
    try:
        message = pymsteams.connectorcard(teams_token)
        message.title("Testing teams webhook by Leaktopus")
        message.text("Testing testing, attention please")
        message.send()
    except pymsteams.TeamsWebhookException as e:
        return str(e)

    return "Sent message"
