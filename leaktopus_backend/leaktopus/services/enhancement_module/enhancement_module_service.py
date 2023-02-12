from leaktopus.details.scan.potential_leak_source_request import PotentialLeakSourceRequest
from leaktopus.services.enhancement_module.enhancement_module_provider import EnhancementModuleProviderInterface
from leaktopus.services.leak.provider_interface import LeakProviderInterface


class EnhancementModuleException(Exception):
    pass


class EnhancementModuleService:
    def __init__(self, enhancement_module_provider: EnhancementModuleProviderInterface):
        self.enhancement_module_provider = enhancement_module_provider

    def get_provider_name(self):
        return self.enhancement_module_provider.get_provider_name()

    def execute(self, potential_leak_source_request: PotentialLeakSourceRequest, leak_service: LeakProviderInterface, repo_path, full_diff_dir):
        return self.enhancement_module_provider.execute(potential_leak_source_request, leak_service, repo_path, full_diff_dir)

