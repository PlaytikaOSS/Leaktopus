from leaktopus.services.notification_factory.provider_interface import NotificationFactoryProviderInterface


class NotificationFactory:
    def __init__(self, provider: NotificationFactoryProviderInterface):
        self.provider = provider

    def new(self, provider_type, **kwargs):
        return self.provider.new(provider_type, **kwargs)
