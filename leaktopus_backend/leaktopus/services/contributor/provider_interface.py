from abc import abstractmethod
from typing import Protocol
from leaktopus.services.contributor.contributor import Contributor


class ContributorProviderInterface(Protocol):
    @abstractmethod
    def get_contributors(self, **kwargs) -> list[Contributor]:
        pass

    @abstractmethod
    def add_contributor(self, leak_id, name, author_email, committer_email, is_organization_domain, **kwargs):
        pass
