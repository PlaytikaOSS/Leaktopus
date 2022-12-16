from abc import abstractmethod
from typing import Protocol


class NotificationFactoryProviderInterface(Protocol):
    @abstractmethod
    def new(self, provider_type, **kwargs):
        pass
