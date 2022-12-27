import json

from celery import shared_task

from leaktopus.app import create_celery_app
from leaktopus.services.notification.notification_service import NotificationException

from leaktopus.tasks.celery.scan.celery_search_results_dispatcher import (
    CelerySearchResultsDispatcher,
)
from leaktopus.tasks.github.scan.github_potential_leak_source_filter import (
    GithubPotentialLeakSourceFilter,
)
from leaktopus.tasks.potential_leak_source_request import PotentialLeakSourceRequest
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.factory import (
    create_leak_service,
    create_notification_service,
    create_alert_service,
    create_ignore_pattern_service,
    create_leaktopus_config_service,
    create_potential_leak_source_scan_status_service,
    create_potential_leak_source_page_results_fetcher,
    create_potential_leak_source_filter,
    create_search_results_dispatcher,
)
from leaktopus.usecases.scan.could_not_fetch_exception import CouldNotFetchException
from leaktopus.usecases.scan.domain_extractor import DomainExtractor
from leaktopus.usecases.scan.email_extractor import EmailExtractor

from leaktopus.usecases.scan.fetch_potential_leak_source_page_use_case import (
    FetchPotentialLeakSourcePageUseCase,
)
from leaktopus.usecases.scan.save_potential_leak_source_page_use_case import (
    SavePotentialLeakSourcePageUseCase,
)
from leaktopus.usecases.scan.search_results_dispatcher_interface import (
    SearchResultsDispatcherInterface,
)
from leaktopus.usecases.scan.trigger_pages_scan_use_case import (
    CollectPotentialLeakSourcePagesUseCase,
)
from leaktopus.utils.common_imports import logger


@shared_task
def send_alerts_notification_task_endpoint():
    leak_service = create_leak_service()
    alert_service = create_alert_service()
    notification_service = create_notification_service()

    try:
        return SendAlertsNotificationTask(
            leak_service, alert_service, notification_service
        ).run()
    except NotificationException as ne:
        logger.warning("Couldn't send alerts notification. Reason: {}", ne)
    except Exception as e:
        logger.error("Error when trying to send alerts notification. Error: {}", e)


@shared_task
def trigger_pages_scan_task_endpoint(
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
    auto_retry_for=(CouldNotFetchException,),
)
def fetch_potential_leak_source_page_task_endpoint(
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
    save_potential_leak_source_page_results_task_endpoint.s(
        page_results=page_results,
        current_page_number=current_page_number,
        number_of_pages=number_of_pages,
        potential_leak_source_request=potential_leak_source_request,
    ).apply_async()


@shared_task
def save_potential_leak_source_page_results_task_endpoint(
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
        gh_get_repos_full_names,
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
        context = json.loads(leak.context)
        repos_full_names.append(context["owner"] + "/" + context["repo_name"])

    chain = (
        leak_enhancer.s(
            repos_full_names=repos_full_names,
            scan_id=potential_leak_source_request.scan_id,
            organization_domains=potential_leak_source_request.organization_domains,
            sensitive_keywords=potential_leak_source_request.sensitive_keywords,
            enhancement_modules=potential_leak_source_request.enhancement_modules,
        )
        | github_index_commits.s(scan_id=potential_leak_source_request.scan_id)
        | update_scan_status_async.s(scan_id=potential_leak_source_request.scan_id)
    )
    chain.apply_async()
