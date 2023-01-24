from leaktopus.services.leaktopus_config.leaktopus_config_provider_interface import (
    LeaktopusConfigProviderInterface,
)


class LeaktopusConfigService:
    def __init__(self, provider: LeaktopusConfigProviderInterface):
        self.provider = provider

    def get_tlds(self) -> list[str]:
        return self.provider.get_tlds()

    def get_max_domain_emails(self) -> int:
        return self.provider.get_max_domain_emails()

    def get_max_non_org_emails(self) -> int:
        return self.provider.get_max_non_org_emails()

    def get_max_fork_count(self) -> int:
        return self.provider.get_max_fork_count()

    def get_max_star_count(self) -> int:
        return self.provider.get_max_star_count()
