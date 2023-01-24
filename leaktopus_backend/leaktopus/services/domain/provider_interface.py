from abc import abstractmethod
from typing import Protocol
from leaktopus.services.domain.domain import Domain


class DomainProviderInterface(Protocol):
    @abstractmethod
    def get_domains(self, **kwargs) -> list[Domain]:
        pass

    @abstractmethod
    def add_domain(self, leak_id, url, domain, **kwargs):
        pass
