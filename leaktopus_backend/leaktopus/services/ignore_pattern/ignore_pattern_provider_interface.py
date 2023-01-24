from abc import abstractmethod
from typing import Protocol


class IgnorePatternProviderInterface(Protocol):
    @abstractmethod
    def get_ignore_patterns(self):
        pass
