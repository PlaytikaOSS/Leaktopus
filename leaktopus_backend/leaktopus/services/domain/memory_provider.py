from leaktopus.services.domain.domain import Domain
from leaktopus.services.domain.provider_interface import (
    DomainProviderInterface,
)
import datetime

class DomainMemoryProvider(DomainProviderInterface):
    def __init__(self, domains=[], override_methods={}):
        self.domains = domains
        self.override_methods = override_methods

    def get_domains(self, **kwargs) -> list[Domain]:
        filtered_domains = self.domains

        for prop, value in kwargs.items():
            filtered_domains = [
                d for d in filtered_domains
                if getattr(d, prop) == value
            ]

        return (
            self.override_methods["get_domains"]()
            if "get_domains" in self.override_methods
            else filtered_domains
        )

    def add_domain(self, leak_id, url, domain, **kwargs):
        pid = len(self.domains)+1
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        domain = Domain(pid, leak_id, url, domain, created_at, **kwargs)

        self.domains.append(domain)
        return (
            self.override_methods["add_domain"]()
            if "add_domain" in self.override_methods
            else pid
        )
