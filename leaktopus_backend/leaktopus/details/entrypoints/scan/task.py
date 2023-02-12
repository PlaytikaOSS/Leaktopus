from celery import shared_task

from leaktopus.details.scan.potential_leak_source_request import (
    PotentialLeakSourceRequest,
)
from leaktopus.factory import (
    create_leak_service,
    create_leaktopus_config_service,
    create_potential_leak_source_scan_status_service,
    create_potential_leak_source_page_results_fetcher,
    create_potential_leak_source_filter,
    create_search_results_dispatcher,
)
from leaktopus.domain.scan.exceptions.could_not_fetch_exception import (
    CouldNotFetchException,
)
from leaktopus.domain.extractors.email_extractor import EmailExtractor

from leaktopus.domain.scan.usecases.fetch_potential_leak_source_page_use_case import (
    FetchPotentialLeakSourcePageUseCase,
)
from leaktopus.domain.scan.usecases.save_potential_leak_source_page_use_case import (
    SavePotentialLeakSourcePageUseCase,
)
from leaktopus.domain.scan.usecases.trigger_pages_scan_use_case import (
    CollectPotentialLeakSourcePagesUseCase,
)
from leaktopus.utils.common_imports import logger


@shared_task
def trigger_pages_scan_task_entrypoint(
    initial_search_metadata,
    potential_leak_source_request: PotentialLeakSourceRequest,
    dispatcher_type: str,
):
    logger.debug(
        "Triggering pages scan for scan_id: {}", potential_leak_source_request.scan_id
    )
    search_results_dispatcher = create_search_results_dispatcher(dispatcher_type)
    potential_leak_source_scan_status_service = (
        create_potential_leak_source_scan_status_service()
    )
    use_case = CollectPotentialLeakSourcePagesUseCase(
        potential_leak_source_scan_status_service=potential_leak_source_scan_status_service,
        search_results_dispatcher=search_results_dispatcher,
    )
    use_case.execute(initial_search_metadata, potential_leak_source_request)


@shared_task(
    bind=True,
    max_retries=200,
    autoretry_for=(CouldNotFetchException,),
)
def fetch_potential_leak_source_page_task_entrypoint(
    self,
    current_page_number,
    results,
    number_of_pages,
    potential_leak_source_request: PotentialLeakSourceRequest,
):
    logger.debug(
        "Fetching page {} for scan_id: {}",
        current_page_number,
        potential_leak_source_request.scan_id,
    )
    potential_leak_source_scan_status_service = (
        create_potential_leak_source_scan_status_service()
    )

    potential_leak_source_page_results_fetcher = (
        create_potential_leak_source_page_results_fetcher(
            potential_leak_source_request.provider_type
        )
    )
    use_case = FetchPotentialLeakSourcePageUseCase(
        potential_leak_source_scan_status_service=potential_leak_source_scan_status_service,
        potential_leak_source_page_results_fetcher=potential_leak_source_page_results_fetcher,
    )
    page_results = use_case.execute(
        results, current_page_number, potential_leak_source_request.scan_id
    )
    save_potential_leak_source_page_results_task_entrypoint.s(
        page_results=page_results,
        current_page_number=current_page_number,
        number_of_pages=number_of_pages,
        potential_leak_source_request=potential_leak_source_request,
    ).apply_async()


@shared_task
def save_potential_leak_source_page_results_task_entrypoint(
    page_results,
    number_of_pages,
    current_page_number,
    potential_leak_source_request: PotentialLeakSourceRequest,
):
    logger.debug(
        "Saving page results for scan_id: {}", potential_leak_source_request.scan_id
    )
    leak_service = create_leak_service()
    email_extractor = EmailExtractor(
        organization_domains=potential_leak_source_request.organization_domains
    )
    leaktopus_config_service = create_leaktopus_config_service()
    potential_leak_source_scan_status_service = (
        create_potential_leak_source_scan_status_service()
    )
    potential_leak_source_filter = create_potential_leak_source_filter(
        potential_leak_source_request.provider_type,
        leak_service=leak_service,
        email_extractor=email_extractor,
        leaktopus_config_service=leaktopus_config_service,
    )
    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter,
        email_extractor=email_extractor,
        potential_leak_source_scan_status_service=potential_leak_source_scan_status_service,
    )
    use_case.execute(
        potential_leak_source_request.scan_id,
        page_results,
        potential_leak_source_request.search_query,
        current_page_number,
    )

    # This part should be refactored. Currently it's a shortcut to support the same behavior as before.
    # The idea is to enhance only if all pages have been scanned i.e set to ANALYZED
    from leaktopus.common.scanner_async import (
        update_scan_status_async,
    )
    from leaktopus.common.github_indexer import github_index_commits
    from leaktopus.common.leak_enhancer import leak_enhancer

    pages_analyzing_count = (
        potential_leak_source_scan_status_service.get_analyzing_count(
            potential_leak_source_request.scan_id
        )
    )
    if pages_analyzing_count < number_of_pages:
        logger.debug(
            "Still not Analyzing leaks for scan_id: {} ({} / {})",
            potential_leak_source_request.scan_id,
            pages_analyzing_count,
            number_of_pages,
        )
        return

    logger.debug(
        "Analyzing leaks for scan_id: {}", potential_leak_source_request.scan_id
    )

    repos_full_names = []
    leaks = leak_service.get_leaks(
        search_query=potential_leak_source_request.search_query
    )
    for leak in leaks:
        repos_full_names.append(leak.context["owner"] + "/" + leak.context["repo_name"])

    chain = (
        leak_enhancer.s(
            repos_full_names=repos_full_names,
            scan_id=potential_leak_source_request.scan_id,
            organization_domains=potential_leak_source_request.organization_domains,
            sensitive_keywords=potential_leak_source_request.sensitive_keywords,
            enhancement_modules=potential_leak_source_request.enhancement_modules,
            potential_leak_source_request=potential_leak_source_request
        )
        | github_index_commits.s(scan_id=potential_leak_source_request.scan_id)
        | update_scan_status_async.s(scan_id=potential_leak_source_request.scan_id)
    )
    chain.apply_async()
