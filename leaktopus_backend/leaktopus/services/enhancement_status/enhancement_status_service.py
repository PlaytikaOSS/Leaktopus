from leaktopus.services.enhancement_status.provider_interface import EnhancementStatusProviderInterface


class EnhancementStatusException(Exception):
    pass


class EnhancementStatusService:
    def __init__(self, enhancement_status_provider: EnhancementStatusProviderInterface):
        self.enhancement_status_provider = enhancement_status_provider

    def get_enhancement_status(self, **kwargs):
        return self.enhancement_status_provider.get_enhancement_status(**kwargs)

    def add_enhancement_status(self, leak_url, search_query, module_key, last_modified, **kwargs):
        return self.enhancement_status_provider.add_enhancement_status(leak_url, search_query, module_key, last_modified, **kwargs)

    def update_enhancement_status(self, id, **kwargs):
        return self.enhancement_status_provider.update_enhancement_status(id, **kwargs)
