import struct
from abc import abstractmethod
from typing import Protocol

import pytest
from celery import Celery, group
from loguru import logger

from leaktopus.models.scan_status import ScanStatus
from leaktopus.tasks.endpoints import crawl_scm_page_task_endpoint


class SCMScannerStatusProviderInterface(Protocol):
    @abstractmethod
    def get_status(self, scan_id: int) -> ScanStatus:
        pass


class SCMScannerStatusService:
    def __init__(self, provider: SCMScannerStatusProviderInterface):
        self.provider = provider

    def is_aborting(self, scan_id: int) -> bool:
        return self.provider.get_status(scan_id) == ScanStatus.SCAN_ABORTING


class CelerySearchResultsFetcher(Protocol):
    def __init__(self):
        self.client = Celery()

    def fetch(self, initial_search_metadata, scan_id, organization_domains):
        tasks = []
        for page_num in initial_search_metadata["num_pages"]:
            tasks.append(
                crawl_scm_page_task_endpoint.s(
                    results=initial_search_metadata["results"],
                    page_num=page_num,
                    scan_id=scan_id,
                )
            )
        result_group = group(tasks).apply_async()


class SearchResultsFetcherInterface(Protocol):
    @abstractmethod
    def fetch(self, initial_search_metadata, scan_id, organization_domains):
        pass


# Replaces github_fetch_pages
class TriggerPagesScanUseCase:
    def __init__(
        self,
        scm_scanner_status_service: SCMScannerStatusService,
        search_results_fetcher: SearchResultsFetcherInterface,
    ):
        self.scm_scanner_status_service = scm_scanner_status_service
        self.search_results_fetcher = search_results_fetcher

    def execute(self, initial_search_metadata, scan_id, organization_domains):
        self.guard_initial_search_metadata(initial_search_metadata)
        self.guard_scan_is_aborting(scan_id)
        self.search_results_fetcher.fetch(
            initial_search_metadata, scan_id, organization_domains
        )

    def guard_initial_search_metadata(self, initial_search_metadata):
        if not initial_search_metadata:
            raise Exception("initial_search_metadata is empty")

        if (
            not initial_search_metadata["results"]
            or len(initial_search_metadata["results"]) == 0
        ):
            raise Exception("initial_search_metadata.results is empty")

        if (
            not initial_search_metadata["num_pages"]
            or initial_search_metadata["num_pages"] == 0
        ):
            raise Exception("initial_search_metadata.num_pages is empty")

    def guard_scan_is_aborting(self, scan_id):
        if self.scm_scanner_status_service.is_aborting(scan_id):
            raise Exception("Scan is aborting")


@pytest.fixture
def search_results_fetcher_mock(mocker):
    return mocker.patch.object(SearchResultsFetcherInterface, "fetch")


@pytest.fixture
def scm_scanner_status_provider_mock(mocker):
    return mocker.patch.object(SCMScannerStatusProviderInterface, "get_status")


@pytest.mark.parametrize(
    "initial_search_metadata",
    [
        {
            "results": [1, 2, 3],
            "num_pages": 2,
        },
    ],
)
def test_should_trigger_pages_scan_successfully(
    search_results_fetcher_mock,
    scm_scanner_status_provider_mock,
    initial_search_metadata,
):
    scan_id = 1
    organization_domains = ["abc.com", "def.com"]

    search_results_fetcher_mock.return_value = None
    scm_scanner_status_provider_mock.get_status.return_value = ScanStatus.SCAN_SEARCHING

    use_case = TriggerPagesScanUseCase(
        scm_scanner_status_service=SCMScannerStatusService(
            provider=scm_scanner_status_provider_mock
        ),
        search_results_fetcher=search_results_fetcher_mock,
    )
    use_case.execute(initial_search_metadata, scan_id, organization_domains)
    search_results_fetcher_mock.fetch.assert_called_with(
        initial_search_metadata, scan_id, organization_domains
    )


@pytest.mark.parametrize(
    "initial_search_metadata",
    [
        None,
        {"num_pages": None},
        {"results": None, "num_pages": None},
        {"results": [], "num_pages": 1},
        {"results": [1], "num_pages": 0},
    ],
)
def test_should_trigger_pages_scan_and_fail(
    search_results_fetcher_mock,
    scm_scanner_status_provider_mock,
    initial_search_metadata,
):
    scan_id = 1
    organization_domains = ["abc.com", "def.com"]

    search_results_fetcher_mock.return_value = None
    scm_scanner_status_provider_mock.get_status.return_value = ScanStatus.SCAN_SEARCHING

    use_case = TriggerPagesScanUseCase(
        scm_scanner_status_service=SCMScannerStatusService(
            provider=scm_scanner_status_provider_mock
        ),
        search_results_fetcher=search_results_fetcher_mock,
    )
    with pytest.raises(Exception):
        use_case.execute(initial_search_metadata, scan_id, organization_domains)


@pytest.mark.parametrize(
    "initial_search_metadata",
    [
        {"results": [1, 2, 3], "num_pages": [1, 2]},
    ],
)
def test_should_trigger_pages_scan_and_fail_when_scan_is_aborting(
    search_results_fetcher_mock,
    scm_scanner_status_provider_mock,
    initial_search_metadata,
):
    scan_id = 1
    organization_domains = ["abc.com", "def.com"]

    search_results_fetcher_mock.return_value = None
    scm_scanner_status_provider_mock.get_status.return_value = ScanStatus.SCAN_ABORTING

    use_case = TriggerPagesScanUseCase(
        scm_scanner_status_service=SCMScannerStatusService(
            provider=scm_scanner_status_provider_mock
        ),
        search_results_fetcher=search_results_fetcher_mock,
    )
    with pytest.raises(Exception):
        use_case.execute(initial_search_metadata, scan_id, organization_domains)
