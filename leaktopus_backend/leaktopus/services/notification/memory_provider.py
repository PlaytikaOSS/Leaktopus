from leaktopus.services.leak.leak import Leak
from leaktopus.services.notification.notification_provider import NotificationProviderInterface
from leaktopus.utils.common_imports import logger


class NotificationMemoryProvider(NotificationProviderInterface):
    def __init__(self, server_url, override_methods={}, **kwargs):
        self.override_methods = override_methods
        self.server_url = server_url

    def get_provider_name(self):
        return "memory"

    def send_notifications(self, leaks: list[Leak]) -> list[Leak]:
        logger.info("Notification service handled {} new leaks", len(leaks))
        return leaks

    def send_test(self):
        logger.info("Test notification was sent (memory)")