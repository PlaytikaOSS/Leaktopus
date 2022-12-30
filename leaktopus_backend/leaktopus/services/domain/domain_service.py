from leaktopus.services.domain.provider_interface import DomainProviderInterface


class DomainException(Exception):
    pass


class DomainService:
    def __init__(self, domain_provider: DomainProviderInterface):
        self.domain_provider = domain_provider

    def get_domains(self, **kwargs):
        return self.domain_provider.get_domains(**kwargs)

    def add_domain(self, leak_id, url, domain, **kwargs):
        return self.domain_provider.add_domain(leak_id, url, domain, **kwargs)
