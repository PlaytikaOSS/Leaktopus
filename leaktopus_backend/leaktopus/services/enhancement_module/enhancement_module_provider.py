from abc import abstractmethod
from typing import Protocol

from leaktopus.details.scan.potential_leak_source_request import PotentialLeakSourceRequest
from leaktopus.services.leak.provider_interface import LeakProviderInterface


class EnhancementModuleProviderInterface(Protocol):
    @abstractmethod
    def get_provider_name(self):
        pass

    @abstractmethod
    def execute(self, potential_leak_source_request: PotentialLeakSourceRequest, leak_service: LeakProviderInterface, repo_path, full_diff_dir):
        pass
