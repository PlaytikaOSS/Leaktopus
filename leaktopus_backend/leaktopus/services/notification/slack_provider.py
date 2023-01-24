from leaktopus.services.leak.leak import Leak
from leaktopus.services.notification.notification_provider import NotificationProviderInterface
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.utils.common_imports import logger
from slack_sdk import WebClient


class NotificationSlackProvider(NotificationProviderInterface):
    def __init__(self, **kwargs):
        self.server_url = kwargs.get("server_url")
        self.integration_token = kwargs.get("integration_token")
        self.channel = kwargs.get("channel")

        if not self.integration_token:
            raise NotificationException("Slack integration token (webhook) is missing.")
        self.client = WebClient(token=self.integration_token)

        if not self.channel:
            raise NotificationException("Slack channel definition is missing.")

    def get_provider_name(self):
        return "slack"

    def send_notifications(self, leaks: list[Leak]) -> list[Leak]:
        for leak in leaks:
            self.client.chat_postMessage(
                channel=self.channel,
                text="A new leak has been found by Leaktopus",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f":droplet:A new leak has been found for the search query: `{leak.search_query}`"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View leak",
                            },
                            "url": f"{self.server_url}/api/leak/{leak.leak_id}",
                            "action_id": "button-action"
                        }
                    }
                ]
            )

        logger.info("Notification service handled {} new leaks", len(leaks))

        return leaks

    def send_test(self):
        self.client.chat_postMessage(
            channel=self.channel,
            text="Testing Slack webhook by Leaktopus",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Testing testing, attention please"
                    }
                }
            ],
        )
        logger.info("Slack test notification has ben sent")
