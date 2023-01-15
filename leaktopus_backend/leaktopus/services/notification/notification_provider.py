from abc import abstractmethod
from typing import Protocol
from leaktopus.services.leak.leak import Leak


class NotificationProviderInterface(Protocol):
    @abstractmethod
    def get_provider_name(self):
        pass

    @abstractmethod
    def send_notifications(self, leaks: list[Leak]) -> list[Leak]:
        pass

    @abstractmethod
    def send_test(self):
        pass
