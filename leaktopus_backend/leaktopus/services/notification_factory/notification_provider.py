from leaktopus.services.notification.ms_teams_provider import MsTeamsProvider
from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.services.notification.slack_provider import SlackProvider
from leaktopus.services.notification_factory.provider_interface import NotificationFactoryProviderInterface


class NotificationFactoryNotificationProvider(NotificationFactoryProviderInterface):
    def __init__(self, options):
        self.options = options

    def new(self, provider_type, **kwargs):
        provider = {
            "ms_teams": MsTeamsProvider,
            "slack": SlackProvider,
        }[provider_type](**kwargs)
        return NotificationService(provider)
