from celery import shared_task

from leaktopus.app import create_celery_app
from leaktopus.common import leak_enhancer
from leaktopus.services.ignore_pattern.ignore_pattern_service import (
    IgnorePatternService,
)
from leaktopus.services.ignore_pattern.sqlite_ignore_pattern_provider import (
    SqliteIgnorePatternProvider,
)
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_service import (
    PotentialLeakSourceScanStatusService,
)

from leaktopus.services.potential_leak_source_scan_status.sqlite_potential_leak_source_scan_status_provider import (
    SqlitePotentialLeakSourceScanStatusProvider,
)

from leaktopus.tasks.celery.scan.celery_search_results_dispatcher import (
    CelerySearchResultsDispatcher,
)
from leaktopus.tasks.github.scan.github_potential_leak_source_filter import (
    GithubPotentialLeakSourceFilter,
)
from leaktopus.tasks.github.scan.github_potential_leak_source_page_results_fetcher import (
    GithubPotentialLeakSourcePageResultsFetcher,
)
from leaktopus.tasks.potential_leak_source_request import PotentialLeakSourceRequest
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.factory import (
    create_leak_service,
    create_notification_service,
    create_alert_service,
    create_ignore_pattern_service,
    create_leaktopus_config_service,
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
    initial_search_metadata, potential_leak_source_request: PotentialLeakSourceRequest
):
    client = create_celery_app()
    logger.debug(
        "Triggering pages scan for scan_id: {}", potential_leak_source_request.scan_id
    )
    use_case = CollectPotentialLeakSourcePagesUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=SqlitePotentialLeakSourceScanStatusProvider()
        ),
        search_results_dispatcher=CelerySearchResultsDispatcher(client=client),
    )
    use_case.execute(initial_search_metadata, potential_leak_source_request)


@shared_task(
    bind=True,
    max_retries=200,
    auto_retry_for=(CouldNotFetchException,),
)
def fetch_potential_leak_source_page_task_endpoint(
    self, results, page_num, potential_leak_source_request: PotentialLeakSourceRequest
):
    client = create_celery_app()
    logger.debug(
        "Fetching page {} for scan_id: {}",
        page_num,
        potential_leak_source_request.scan_id,
    )
    use_case = FetchPotentialLeakSourcePageUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=SqlitePotentialLeakSourceScanStatusProvider()
        ),
        potential_leak_source_page_results_fetcher=GithubPotentialLeakSourcePageResultsFetcher(),
    )
    page_results = use_case.execute(
        results, page_num, potential_leak_source_request.scan_id
    )
    save_potential_leak_source_page_results_task_endpoint.s(
        page_results=page_results,
        potential_leak_source_request=potential_leak_source_request,
    ).apply_async()


@shared_task
def save_potential_leak_source_page_results_task_endpoint(
    page_results, potential_leak_source_request: PotentialLeakSourceRequest
):
    logger.debug(
        "Saving page results for scan_id: {}", potential_leak_source_request.scan_id
    )
    leak_service = create_leak_service()
    ignore_pattern_service = create_ignore_pattern_service()
    email_extractor = EmailExtractor(
        organization_domains=potential_leak_source_request.organization_domains
    )
    leaktopus_config_service = create_leaktopus_config_service()
    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=GithubPotentialLeakSourceFilter(
            leak_service=leak_service,
            ignore_pattern_service=ignore_pattern_service,
            domain_extractor=DomainExtractor(tlds=leaktopus_config_service.get_tlds()),
            email_extractor=email_extractor,
            leaktopus_config_service=leaktopus_config_service,
        ),
        email_extractor=email_extractor,
    )
    use_case.execute(
        potential_leak_source_request.scan_id,
        page_results,
        potential_leak_source_request.search_query,
    )

    from leaktopus.common.scanner_async import (
        gh_get_repos_full_names,
        update_scan_status_async,
    )
    from leaktopus.common.github_indexer import github_index_commits

    chain = (
        gh_get_repos_full_names.s()
        | leak_enhancer.s(
            scan_id=potential_leak_source_request.scan_id,
            organization_domains=potential_leak_source_request.organization_domains,
            sensitive_keywords=potential_leak_source_request.sensitive_keywords,
            enhancement_modules=potential_leak_source_request.enhancement_modules,
        )
        | github_index_commits.s(scan_id=potential_leak_source_request.scan_id)
        | update_scan_status_async.s(scan_id=potential_leak_source_request.scan_id)
    )
