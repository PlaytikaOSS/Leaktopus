from abc import abstractmethod
from typing import Protocol

from leaktopus.services.ignore_pattern.ignore_pattern_provider_interface import (
    IgnorePatternProviderInterface,
)


class SqliteIgnorePatternProvider(IgnorePatternProviderInterface):
    def get_ignore_patterns(self):
        pass
