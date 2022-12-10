from abc import abstractmethod
from typing import Protocol
from leaktopus.services.alert.alert import Alert


class AlertProviderInterface(Protocol):
    @abstractmethod
    def get_alerts(self, **kwargs) -> list[Alert]:
        pass

    @abstractmethod
    def add_alert(self, leak_id, type, **kwargs):
        pass
