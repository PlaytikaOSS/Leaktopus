from leaktopus.services.leak.provider_interface import    LeakProviderInterface


class LeakException(Exception):
    pass


class LeakService:
    def __init__(self, leak_provider: LeakProviderInterface):
        self.leak_provider = leak_provider

    def get_leaks(self, **kwargs):
        return self.leak_provider.get_leaks(**kwargs)

    def add_leak(self, url, search_query, leak_type, context, leaks, acknowledged, last_modified, **kwargs):
        return self.leak_provider.add_leak(url, search_query, leak_type, context, leaks, acknowledged, last_modified, **kwargs)

    def save_leaks(self, leaks):
        return self.leak_provider.save_leaks(leaks)
    def update_leak(self, leak_id, **kwargs):
        return self.leak_provider.update_leak(leak_id, **kwargs)

    def delete_leak_by_url(self, url, **kwargs):
        return self.leak_provider.delete_leak_by_url(url, **kwargs)
