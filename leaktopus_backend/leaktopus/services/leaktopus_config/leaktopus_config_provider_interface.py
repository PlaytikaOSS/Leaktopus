from abc import abstractmethod
from typing import Protocol


class LeaktopusConfigProviderInterface(Protocol):
    @abstractmethod
    def get_tlds(self) -> list[str]:
        pass

    @abstractmethod
    def get_max_domain_emails(self) -> int:
        pass

    @abstractmethod
    def get_max_non_org_emails(self) -> int:
        pass

    @abstractmethod
    def get_max_fork_count(self) -> int:
        pass

    @abstractmethod
    def get_max_star_count(self) -> int:
        pass
