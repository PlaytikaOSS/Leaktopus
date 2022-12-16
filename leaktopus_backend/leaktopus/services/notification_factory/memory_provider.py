from leaktopus.services.notification.memory_provider import NotificationMemoryProvider
from leaktopus.services.notification.notification_service import NotificationService
from leaktopus.services.notification_factory.provider_interface import NotificationFactoryProviderInterface


class NotificationFactoryMemoryProvider(NotificationFactoryProviderInterface):
    def __init__(self, override_methods={}):
        self.override_methods = override_methods

    def new(self, provider_type, **kwargs):
        notification_service = NotificationService(
            NotificationMemoryProvider(
                override_methods=self.override_methods,
                server_url="https://localhost",
            )
        )
        return (
            self.override_methods["new"](provider_type, **kwargs)
            if "new" in self.override_methods
            else notification_service
        )
