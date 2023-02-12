from leaktopus.services.enhancement_module.enhancement_module_provider import EnhancementModuleProviderInterface
from leaktopus.utils.common_imports import logger


class EnhancementModuleMemoryProvider(EnhancementModuleProviderInterface):
    def __init__(self, override_methods={}, **kwargs):
        self.override_methods = override_methods

    def get_provider_name(self):
        return "memory"

    def execute(self, potential_leak_source_request, leak_service, url, full_diff_dir):
        logger.info("Enhancement module service is enhancing PLS {} stored in {}", url, full_diff_dir)
