from leaktopus.services.ignore_pattern.ignore_pattern_provider_interface import (
    IgnorePatternProviderInterface,
)


class IgnorePatternService:
    def __init__(self, provider: IgnorePatternProviderInterface):
        self.provider = provider

    def get_ignore_patterns(self):
        return self.provider.get_ignore_patterns()
