import pytest

from leaktopus.models.scan_status import ScanStatus
from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.usecases.scan.fetch_potential_leak_source_page_use_case import (
    FetchPotentialLeakSourcePageUseCase,
)

from leaktopus.usecases.scan.potential_leak_source_page_results_fetcher_interface import (
    PotentialLeakSourcePageResultsFetcherInterface,
)
from leaktopus.usecases.scan.potential_leak_source_page_results_saver_interface import (
    PotentialLeakSourcePageResultsSaverInterface,
)


def test_should_fetch_potential_leak_source_page_successfully(
    potential_leak_source_scan_status_provider_mock,
    potential_leak_source_page_results_fetcher_mock,
    potential_leak_source_page_results_saver_mock,
):
    results = [1, 2, 3]
    page_num = 2
    scan_id = 1
    fetcher_results = [4, 5, 6]

    potential_leak_source_scan_status_provider_mock.get_status.return_value = (
        ScanStatus.SCAN_SEARCHING
    )
    potential_leak_source_page_results_saver_mock.save.return_value = None
    potential_leak_source_page_results_fetcher_mock.fetch.return_value = fetcher_results

    use_case = FetchPotentialLeakSourcePageUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
        potential_leak_source_page_results_fetcher=potential_leak_source_page_results_fetcher_mock,
        potential_leak_source_page_results_saver=potential_leak_source_page_results_saver_mock,
    )
    use_case.execute(results, page_num, scan_id)
    potential_leak_source_page_results_saver_mock.save.assert_called_with(
        fetcher_results, scan_id
    )


@pytest.fixture
def potential_leak_source_page_results_saver_mock(mocker):
    return mocker.patch.object(PotentialLeakSourcePageResultsSaverInterface, "save")


@pytest.fixture
def potential_leak_source_page_results_fetcher_mock(mocker):
    return mocker.patch.object(PotentialLeakSourcePageResultsFetcherInterface, "fetch")
