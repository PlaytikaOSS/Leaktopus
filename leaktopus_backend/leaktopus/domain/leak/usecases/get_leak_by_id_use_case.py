import json

from leaktopus.services.contributor.provider_interface import ContributorProviderInterface
from leaktopus.services.domain.provider_interface import DomainProviderInterface
from leaktopus.services.leak.provider_interface import LeakProviderInterface
from leaktopus.services.potential_leak_source_scan_status.service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.details.scan.potential_leak_source_request import (
    PotentialLeakSourceRequest,
)
from leaktopus.domain.scan.contracts.search_results_dispatcher_interface import (
    SearchResultsDispatcherInterface,
)
from leaktopus.services.secret.provider_interface import SecretProviderInterface
from leaktopus.services.sensitive_keyword.provider_interface import SensitiveKeywordProviderInterface


class GetLeakByIdUseCase:
    def __init__(
            self,
            leak_service: LeakProviderInterface,
            secret_service: SecretProviderInterface,
            domain_service: DomainProviderInterface,
            contributor_service: ContributorProviderInterface,
            sensitive_keyword_service: SensitiveKeywordProviderInterface
    ):
        self.leak_service = leak_service
        self.secret_service = secret_service
        self.domain_service = domain_service
        self.contributor_service = contributor_service
        self.sensitive_keyword_service = sensitive_keyword_service

    def execute(
            self,
            leak_id):

        leaks = self.leak_service.get_leaks(leak_id=leak_id)
        if len(leaks) == 0:
            return []

        leak = leaks[0].to_dict()

        # Get related data to return with the leak.
        leak["secrets"] = self.secret_service.get_secrets(leak_id=leak_id)
        leak["domains"] = self.domain_service.get_domains(leak_id=leak_id)
        leak["contributors"] = self.contributor_service.get_contributors(leak_id=leak_id)
        leak["sensitive_keywords"] = self.sensitive_keyword_service.get_sensitive_keywords(leak_id=leak_id)

        return leak
