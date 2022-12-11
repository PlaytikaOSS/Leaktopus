from leaktopus.services.leak.leak import Leak
from leaktopus.services.notification.notification_provider import NotificationProviderInterface


class NotificationException(Exception):
    pass


class NotificationService:
    def __init__(self, notification_provider: NotificationProviderInterface):
        self.notification_provider = notification_provider

    def get_provider_name(self):
        return self.notification_provider.get_provider_name()

    def send_notifications(self, leaks: list[Leak]) -> list[Leak]:
        return self.notification_provider.send_notifications(leaks)

    def send_test(self):
        return self.notification_provider.send_test()
