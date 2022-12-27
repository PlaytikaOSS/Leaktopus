import pytest

from leaktopus.models.scan_status import ScanStatus
from leaktopus.services.potential_leak_source_scan_status.service import (
    PotentialLeakSourceScanStatusService,
)
from .fetch_potential_leak_source_page_use_case import (
    FetchPotentialLeakSourcePageUseCase,
)

from leaktopus.domain.scan.contracts.potential_leak_source_page_results_fetcher_interface import (
    PotentialLeakSourcePageResultsFetcherInterface,
)


def test_should_fetch_potential_leak_source_page_successfully(
    potential_leak_source_scan_status_provider_mock,
    potential_leak_source_page_results_fetcher_mock,
):
    results = [1, 2, 3]
    page_number = 2
    scan_id = 1
    fetcher_results = [4, 5, 6]

    potential_leak_source_scan_status_provider_mock.get_status.return_value = (
        ScanStatus.SCAN_SEARCHING
    )
    potential_leak_source_page_results_fetcher_mock.fetch.return_value = fetcher_results

    use_case = FetchPotentialLeakSourcePageUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
        potential_leak_source_page_results_fetcher=potential_leak_source_page_results_fetcher_mock,
    )
    page_results = use_case.execute(results, page_number, scan_id)
    assert page_results == fetcher_results


@pytest.fixture
def potential_leak_source_page_results_fetcher_mock(mocker):
    return mocker.patch.object(PotentialLeakSourcePageResultsFetcherInterface, "fetch")
