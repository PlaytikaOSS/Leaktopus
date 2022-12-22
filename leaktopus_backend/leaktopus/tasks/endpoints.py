from celery import shared_task

from leaktopus.app import create_celery_app
from leaktopus.services.notification.notification_service import NotificationException
from leaktopus.tasks.send_alerts_notification_task import SendAlertsNotificationTask
from leaktopus.factory import (
    create_leak_service,
    create_notification_service,
    create_alert_service,
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
    use_case = TriggerPagesScanUseCase(
        scm_scanner_status_service=SCMScannerStatusService(),
        search_results_fetcher=CelerySearchResultsFetcher(),
    )
    use_case.execute(initial_search_metadata, scan_id, organization_domains)


@shared_task(bind=True, max_retries=200)
def crawl_scm_page_task_endpoint(self, results, page_num, scan_id):
    try:
        use_case = CrawlerAndSaveScmPageUseCase()
        use_case.execute(results, page_num, scan_id)
    except Exception as e:
        logger.error("Error when trying to crawl and save SCM page. Error: {}", e)
        raise self.retry(exc=e, countdown=10)
