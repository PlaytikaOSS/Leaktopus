from abc import abstractmethod
from typing import Protocol
from leaktopus.services.secret.secret import Secret


class SecretProviderInterface(Protocol):
    @abstractmethod
    def get_secrets(self, **kwargs) -> list[Secret]:
        pass

    @abstractmethod
    def add_secret(self, leak_id, url, signature_name, match_string, **kwargs):
        pass
