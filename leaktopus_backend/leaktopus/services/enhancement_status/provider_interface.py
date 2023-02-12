from abc import abstractmethod
from typing import Protocol
from leaktopus.services.enhancement_status.enhancement_status import EnhancementStatus


class EnhancementStatusProviderInterface(Protocol):
    @abstractmethod
    def get_enhancement_status(self, **kwargs) -> list[EnhancementStatus]:
        pass

    @abstractmethod
    def add_enhancement_status(self, leak_url, search_query, module_key, last_modified, **kwargs) -> int:
        pass

    @abstractmethod
    def update_enhancement_status(self, id, **kwargs) -> EnhancementStatus:
        pass