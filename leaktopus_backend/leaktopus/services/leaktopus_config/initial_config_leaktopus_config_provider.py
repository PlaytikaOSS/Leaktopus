from leaktopus.services.leaktopus_config.leaktopus_config_provider_interface import (
    LeaktopusConfigProviderInterface,
)


class InitialConfigLeaktopusConfigProvider(LeaktopusConfigProviderInterface):
    def __init__(self, config, provider: LeaktopusConfigProviderInterface = None):
        self.config = config

    def get_tlds(self) -> list[str]:
        return self.config["tlds"]

    def get_max_domain_emails(self) -> int:
        return self.config["max_domain_emails"]

    def get_max_non_org_emails(self) -> int:
        return self.config["max_non_org_emails"]

    def get_max_fork_count(self) -> int:
        return self.config["max_fork_count"]

    def get_max_star_count(self) -> int:
        return self.config["max_star_count"]
