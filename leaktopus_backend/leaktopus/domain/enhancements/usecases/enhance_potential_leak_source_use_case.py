from leaktopus.utils.common_imports import logger
from leaktopus.details.scan.potential_leak_source_request import PotentialLeakSourceRequest
from leaktopus.services.enhancement_module.enhancement_module_provider import EnhancementModuleProviderInterface
from leaktopus.services.enhancement_status.provider_interface import EnhancementStatusProviderInterface
from leaktopus.services.leak.provider_interface import LeakProviderInterface


class EnhancePotentialLeakSourceUseCase:
    def __init__(
            self,
            leak_service: LeakProviderInterface,
            enhancement_status_service: EnhancementStatusProviderInterface,
            enhancement_module_services: list[EnhancementModuleProviderInterface]
    ):
        self.leak_service = leak_service
        self.enhancement_status_service = enhancement_status_service
        self.enhancement_module_services = enhancement_module_services

    def execute(self, potential_leak_source_request: PotentialLeakSourceRequest, leak_url, full_diff_dir):
        enhancement_statuses = []

        leaks = self.leak_service.get_leaks(
            search_query=potential_leak_source_request.search_query,
            url=leak_url,
            acknowledged=False
        )

        if not leaks:
            logger.error("No leaks found for the enrichment of leak_url: {}", leak_url)
            return enhancement_statuses

        leak_last_modified = leaks[0].last_modified

        for lem in self.enhancement_module_services:
            module_key = lem.get_provider_name()
            leak_enhancement_status = self.enhancement_status_service.get_enhancement_status(
                leak_url=leak_url,
                search_query=potential_leak_source_request.search_query,
                module_key=module_key
            )

            if leak_enhancement_status:
                if not leak_last_modified > leak_enhancement_status[0].last_modified:
                    logger.debug("Leak {} was not modified since last scan, skipping enhancement.", leaks[0].leak_id)
                    continue

                logger.debug("Leak {} was modified since last scan and is now enhancing with {}.", leaks[0].leak_id, module_key)
                es_id = self.enhancement_status_service.update_enhancement_status(
                    leak_enhancement_status[0].id,
                    last_modified=leak_last_modified
                )
            else:
                logger.debug("Leak {} first time enhancement with module {}.", leaks[0].leak_id, module_key)
                es_id = self.enhancement_status_service.add_enhancement_status(
                    leak_url,
                    potential_leak_source_request.search_query,
                    lem.get_provider_name(),
                    leak_last_modified
                )

            enhancement_statuses.append(es_id)
            lem.execute(potential_leak_source_request, self.leak_service, leak_url, full_diff_dir)

        return enhancement_statuses
