from celery import shared_task

from leaktopus.app import create_celery_app
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_service import (
    PotentialLeakSourceScanStatusService,
)

from leaktopus.services.potential_leak_source_scan_status.sqlite_potential_leak_source_scan_status_provider import (
    SqlitePotentialLeakSourceScanStatusProvider,
)
from leaktopus.tasks.celery.scan.celery_potential_leak_source_page_results_fetcher import (
    CeleryPotentialLeakSourcePageResultsFetcher,
)
from leaktopus.tasks.celery.scan.celery_potential_leak_source_page_results_saver import (
    CeleryPotentialLeakSourcePageResultsSaver,
)
from leaktopus.tasks.celery.scan.celery_search_results_dispatcher import (
    CelerySearchResultsDispatcher,
)
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.factory import (
    create_leak_service,
    create_notification_service,
    create_alert_service,
)
from leaktopus.usecases.scan.could_not_fetch_exception import CouldNotFetchException

from leaktopus.usecases.scan.fetch_potential_leak_source_page_use_case import (
    FetchPotentialLeakSourcePageUseCase,
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
        logger.errpr("Error when trying to send alerts notification. Error: {}", e)


@shared_task
def trigger_pages_scan_task_endpoint(
    initial_search_metadata, scan_id, organization_domains
):
    client = create_celery_app()
    logger.debug("Triggering pages scan for scan_id: {}", scan_id)
    use_case = CollectPotentialLeakSourcePagesUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=SqlitePotentialLeakSourceScanStatusProvider()
        ),
        search_results_dispatcher=CelerySearchResultsDispatcher(client=client),
    )
    use_case.execute(initial_search_metadata, scan_id, organization_domains)


@shared_task(
    bind=True,
    max_retries=200,
    auto_retry_for=(CouldNotFetchException,),
)
def fetch_potential_leak_source_page_task_endpoint(self, results, page_num, scan_id):
    client = create_celery_app()
    logger.debug("Fetching page {} for scan_id: {}", page_num, scan_id)
    use_case = FetchPotentialLeakSourcePageUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=SqlitePotentialLeakSourceScanStatusProvider()
        ),
        potential_leak_source_page_results_fetcher=CeleryPotentialLeakSourcePageResultsFetcher(),
        potential_leak_source_page_results_saver=CeleryPotentialLeakSourcePageResultsSaver(
            client=client
        ),
    )
    logger.debug("Fetching page {} for scan_id: {}", page_num, scan_id)
    response = use_case.execute(results, page_num, scan_id)
    return response


@shared_task
def save_potential_leak_source_page_results_task_endpoint(page_results, scan_id):
    logger.debug("Saving page results for scan_id: {}", scan_id)
    # use_case = SaveSCMPageResultsUseCase()
    # use_case.execute(page_results, scan_id)
