from leaktopus.services.leak.leak import Leak
from leaktopus.services.notification.notification_provider import NotificationProviderInterface
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.utils.common_imports import logger
import pymsteams


class NotificationMsTeamsProvider(NotificationProviderInterface):
    def __init__(self, **kwargs):
        self.server_url = kwargs.get("server_url")
        self.integration_token = kwargs.get("integration_token")

        if not self.integration_token:
            raise NotificationException("MS Teams integration token (webhook) is missing.")

    def get_provider_name(self):
        return "ms_teams"

    def send_notifications(self, leaks: list[Leak]) -> list[Leak]:
        for leak in leaks:
            message = pymsteams.connectorcard(self.integration_token)
            message.title("A new leak has been found by Leaktopus")
            message.text(f"A new leak has been found for the search query: {leak.search_query}")
            message.addLinkButton("Click here to view leak ",
                                  f"{self.server_url}/api/leak/{leak.leak_id}")
            message.send()

        logger.info("Notification service handled {} new leaks", len(leaks))

        return leaks

    def send_test(self):
        message = pymsteams.connectorcard(self.integration_token)
        message.title("Testing teams webhook by Leaktopus")
        message.text("Testing testing, attention please")
        message.send()

        logger.info("MS teams test notification has ben sent")
