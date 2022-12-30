from abc import abstractmethod
from typing import Protocol
from leaktopus.services.sensitive_keyword.sensitive_keyword import SensitiveKeyword


class SensitiveKeywordProviderInterface(Protocol):
    @abstractmethod
    def get_sensitive_keywords(self, **kwargs) -> list[SensitiveKeyword]:
        pass

    @abstractmethod
    def add_sensitive_keyword(self, leak_id, keyword, url, **kwargs):
        pass
