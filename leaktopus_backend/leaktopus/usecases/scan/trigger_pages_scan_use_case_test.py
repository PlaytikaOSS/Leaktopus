import pytest

from leaktopus.models.scan_status import ScanStatus
from leaktopus.services.potential_leak_source_scan_status.potential_leak_source_scan_status_service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.tasks.potential_leak_source_request import PotentialLeakSourceRequest

from leaktopus.usecases.scan.search_results_dispatcher_interface import (
    SearchResultsDispatcherInterface,
)
from leaktopus.usecases.scan.trigger_pages_scan_use_case import (
    CollectPotentialLeakSourcePagesUseCase,
)


@pytest.fixture
def search_results_dispatcher_mock(mocker):
    return mocker.patch.object(SearchResultsDispatcherInterface, "dispatch")


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
    search_results_dispatcher_mock,
    potential_leak_source_scan_status_provider_mock,
    initial_search_metadata,
):
    scan_id = 1
    organization_domains = ["abc.com", "def.com"]
    potential_leak_source_request = PotentialLeakSourceRequest(
        scan_id=scan_id,
        search_query="",
        organization_domains=organization_domains,
        enhancement_modules=[],
        sensitive_keywords=[],
    )
    search_results_dispatcher_mock.return_value = None
    potential_leak_source_scan_status_provider_mock.get_status.return_value = (
        ScanStatus.SCAN_SEARCHING
    )

    use_case = CollectPotentialLeakSourcePagesUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
        search_results_dispatcher=search_results_dispatcher_mock,
    )
    use_case.execute(initial_search_metadata, potential_leak_source_request)
    search_results_dispatcher_mock.dispatch.assert_called_with(
        initial_search_metadata, potential_leak_source_request
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
    search_results_dispatcher_mock,
    potential_leak_source_scan_status_provider_mock,
    initial_search_metadata,
):
    scan_id = 1
    organization_domains = ["abc.com", "def.com"]

    search_results_dispatcher_mock.return_value = None
    potential_leak_source_scan_status_provider_mock.get_status.return_value = (
        ScanStatus.SCAN_SEARCHING
    )

    use_case = CollectPotentialLeakSourcePagesUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
        search_results_dispatcher=search_results_dispatcher_mock,
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
    search_results_dispatcher_mock,
    potential_leak_source_scan_status_provider_mock,
    initial_search_metadata,
):
    scan_id = 1
    organization_domains = ["abc.com", "def.com"]
    potential_leak_source_request = PotentialLeakSourceRequest(
        scan_id=scan_id,
        search_query="",
        organization_domains=organization_domains,
        enhancement_modules=[],
        sensitive_keywords=[],
    )

    search_results_dispatcher_mock.return_value = None
    potential_leak_source_scan_status_provider_mock.get_status.return_value = (
        ScanStatus.SCAN_ABORTING
    )

    use_case = CollectPotentialLeakSourcePagesUseCase(
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
        search_results_dispatcher=search_results_dispatcher_mock,
    )
    with pytest.raises(Exception):
        use_case.execute(initial_search_metadata, potential_leak_source_request)
