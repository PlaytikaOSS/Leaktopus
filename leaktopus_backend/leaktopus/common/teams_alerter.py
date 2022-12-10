import pymsteams
import os


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
