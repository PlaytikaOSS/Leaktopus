import pymsteams
import os

from leaktopus.services.notification.notification_service import NotificationException


def teams_webhook_test():
    teams_token = os.environ.get('TEAMS_WEBHOOK_URL')
    if not teams_token:
        raise NotificationException("Error: Teams webhook is missing.")

    message = pymsteams.connectorcard(teams_token)
    message.title("Testing teams webhook by Leaktopus")
    message.text("Testing testing, attention please")
    message.send()
