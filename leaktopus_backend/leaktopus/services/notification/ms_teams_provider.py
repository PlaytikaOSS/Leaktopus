from leaktopus.services.leak.leak import Leak
from leaktopus.services.notification.notification_provider import NotificationProviderInterface
from leaktopus.utils.common_imports import logger
import pymsteams


class MsTeamsProvider(NotificationProviderInterface):
    def __init__(self, server_url, integration_token, **kwargs):
        self.server_url = server_url
        self.integration_token = integration_token

    def get_provider_name(self):
        return "ms_teams"

    def send_notifications(self, leaks: list[Leak]) -> list[Leak]:
        for leak in leaks:
            message = pymsteams.connectorcard(self.integration_token)
            message.title("A new leak has been found by Leaktopus")
            message.text(f"A new leak has been found for the search query: {leak['search_query']}")
            message.addLinkButton("Click here to view leak ",
                                  f"{self.server_url}/api/leak/{leak['pid']}")
            message.send()

        logger.info("Notification service handled {} new leaks", len(leaks))

        return leaks

    def send_test(self):
        logger.info("Sent MS teams test notification")
