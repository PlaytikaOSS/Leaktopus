import pytest
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.provider_interface import LeakProviderInterface
from leaktopus.services.potential_leak_source_scan_status.interface import (
    PotentialLeakSourceScanStatusProviderInterface,
)
from leaktopus.services.potential_leak_source_scan_status.service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.domain.extractors.email_extractor import EmailExtractor
from leaktopus.domain.scan.entities.potential_leak_source import PotentialLeakSource
from leaktopus.domain.scan.contracts.potential_leak_source_filter_interface import (
    PotentialLeakSourceFilterInterface,
)
from .save_potential_leak_source_page_use_case import (
    SavePotentialLeakSourcePageUseCase,
)


def test_should_save_potential_leak_source_page_successfully(
    leak_provider_mock,
    ignore_pattern_provider_mock,
    potential_leak_source_filter_mock,
    page_results,
    potential_leak_source_scan_status_provider_mock,
):
    search_query = "test"
    scan_id = 1
    current_page_number = 1

    leak_provider_mock.add_leak.return_value = None
    ignore_pattern_provider_mock.get_ignore_patterns.return_value = []
    potential_leak_source_filter_mock.filter.return_value = True
    potential_leak_source_scan_status_provider_mock.mark_as_analyzing.return_value = (
        None
    )

    leak_service = LeakService(leak_provider=leak_provider_mock)
    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter_mock,
        email_extractor=EmailExtractor(organization_domains=["test.com", "test2.com"]),
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
    )
    use_case.execute(scan_id, page_results, search_query, current_page_number)
    leak_provider_mock.add_leak.assert_called()


def assert_potential_leak_source_modified_for_acknowledged_leak_should_save_new_leak_with_success(
        leak_service,
        potential_leak_source_filter_mock,
        potential_leak_source_scan_status_provider_mock,
        scan_id,
        search_query
):
    current_page_number = 1
    new_last_modified = "Fri, 06 Jan 2023 09:00:00 UTC"
    pls_url = "url_repo_1"
    page_results = [
        PotentialLeakSource(
            url=pls_url,
            name="name_iol_new_1",
            html_url="html_url_iol_new_1",
            last_modified=new_last_modified,
            content="content_iol_new_1",
            context={
                "stargazers_count": 2,
                "forks_count": 2,
            },
            source="source_1",
        ),
    ]

    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter_mock,
        email_extractor=EmailExtractor(organization_domains=["test.com", "test2.com"]),
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
    )
    use_case.execute(scan_id + 1, page_results, search_query, current_page_number)
    saved_leaks_non_ack = leak_service.get_leaks(url=pls_url, acknowledged=False)
    saved_leaks_ack = leak_service.get_leaks(url=pls_url, acknowledged=True)

    # Assert two leaks were saved.
    assert len(saved_leaks_non_ack) == 1
    assert len(saved_leaks_ack) == 1


def assert_unmodified_potential_leak_source_for_acknowledged_leak_should_not_modify_leaks(
        leak_service,
        potential_leak_source_filter_mock,
        potential_leak_source_scan_status_provider_mock,
        page_results_subset,
        scan_id,
        search_query
):
    current_page_number = 1
    subject_potential_leak_source = page_results_subset[0]

    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter_mock,
        email_extractor=EmailExtractor(organization_domains=["test.com", "test2.com"]),
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
    )
    use_case.execute(scan_id + 1, page_results_subset, search_query, current_page_number)
    saved_leaks = leak_service.get_leaks(url=subject_potential_leak_source.url)

    assert len(saved_leaks) == 1


def assert_acknowledged_leak_handled_with_success(
        leak_service,
        potential_leak_source_filter_mock,
        potential_leak_source_scan_status_provider_mock,
        page_results,
        scan_id,
        search_query
):
    subject_potential_leak_source = page_results[1]
    page_results_subset = [subject_potential_leak_source]

    saved_leak = leak_service.get_leaks(url=subject_potential_leak_source.url)[0]
    leak_service.update_leak(saved_leak.leak_id, acknowledged=True)

    assert_unmodified_potential_leak_source_for_acknowledged_leak_should_not_modify_leaks(
        leak_service,
        potential_leak_source_filter_mock,
        potential_leak_source_scan_status_provider_mock,
        page_results_subset,
        scan_id,
        search_query
    )

    assert_potential_leak_source_modified_for_acknowledged_leak_should_save_new_leak_with_success(
        leak_service,
        potential_leak_source_filter_mock,
        potential_leak_source_scan_status_provider_mock,
        scan_id,
        search_query
    )


def assert_leak_context_is_updated_with_success(saved_leaks):
    assert saved_leaks[0].context["stargazers_count"] == 1
    assert saved_leaks[0].context["forks_count"] == 1


def test_should_save_potential_leak_source_page_with_multiple_iols_support(
    factory_leak_service,
    ignore_pattern_provider_mock,
    potential_leak_source_filter_mock,
    page_results,
    potential_leak_source_scan_status_provider_mock,
):
    search_query = "test"
    scan_id = 1
    current_page_number = 1

    ignore_pattern_provider_mock.get_ignore_patterns.return_value = []
    potential_leak_source_filter_mock.filter.return_value = True
    potential_leak_source_scan_status_provider_mock.mark_as_analyzing.return_value = (
        None
    )

    leak_service = factory_leak_service()
    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter_mock,
        email_extractor=EmailExtractor(organization_domains=["test.com", "test2.com"]),
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
    )
    use_case.execute(scan_id, page_results, search_query, current_page_number)
    saved_leaks = leak_service.get_leaks()

    # Assert two leaks were saved.
    assert len(saved_leaks) == 2

    # Assert the first leak has two IOLs.
    assert len(saved_leaks[0].IOL) == 2

    assert_leak_context_is_updated_with_success(saved_leaks)

    assert_acknowledged_leak_handled_with_success(
        leak_service,
        potential_leak_source_filter_mock,
        potential_leak_source_scan_status_provider_mock,
        page_results,
        scan_id,
        search_query
    )


def test_should_raise_exception_when_multiple_non_acknowledged_leaks_matched_for_save(
        factory_leak_service,
        ignore_pattern_provider_mock,
        potential_leak_source_filter_mock,
        page_results,
        potential_leak_source_scan_status_provider_mock,
):
    pass


def test_should_support_multiple_search_queries(
    factory_leak_service,
    ignore_pattern_provider_mock,
    potential_leak_source_filter_mock,
    page_results,
    potential_leak_source_scan_status_provider_mock,
):
    search_query_1 = "search.query.1"
    search_query_2 = "search.query.2"
    scan_id = 1
    current_page_number = 1

    # leak_provider_mock.add_leak.return_value = None
    ignore_pattern_provider_mock.get_ignore_patterns.return_value = []
    potential_leak_source_filter_mock.filter.return_value = True
    potential_leak_source_scan_status_provider_mock.mark_as_analyzing.return_value = (
        None
    )

    leak_service = factory_leak_service()
    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter_mock,
        email_extractor=EmailExtractor(organization_domains=["test.com", "test2.com"]),
        potential_leak_source_scan_status_service=PotentialLeakSourceScanStatusService(
            provider=potential_leak_source_scan_status_provider_mock
        ),
    )

    use_case.execute(scan_id, page_results, search_query_1, current_page_number)
    use_case.execute(scan_id + 1, page_results, search_query_2, current_page_number)
    saved_leaks_1 = leak_service.get_leaks(search_query=search_query_1)
    saved_leaks_2 = leak_service.get_leaks(search_query=search_query_2)

    # Assert two leaks were saved.
    assert len(saved_leaks_1) == 2
    assert len(saved_leaks_2) == 2


@pytest.fixture
def potential_leak_source_scan_status_provider_mock(mocker):
    return mocker.patch.object(
        PotentialLeakSourceScanStatusProviderInterface, "mark_as_analyzing"
    )


@pytest.fixture
def leak_provider_mock(mocker):
    return mocker.patch.object(LeakProviderInterface, "add_leak")


@pytest.fixture
def potential_leak_source_filter_mock(mocker):
    return mocker.patch.object(PotentialLeakSourceFilterInterface, "filter")


@pytest.fixture
def page_results():
    return [
        PotentialLeakSource(
            url="url_repo_1",
            name="name_iol_1",
            html_url="html_url_iol_1",
            last_modified="Sat, 19 Dec 2022 15:34:56 UTC",
            content="content_iol_1 leaktopus@test.com",
            context={
                "stargazers_count": 0,
                "forks_count": 0,
            },
            source="source_1",
        ),
        # Same IOL and repo as the first, but modified context.
        PotentialLeakSource(
            url="url_repo_1",
            name="name_iol_1",
            html_url="html_url_iol_1",
            last_modified="Sat, 19 Dec 2022 15:34:56 UTC",
            content="content_iol_1 leaktopus@test.com",
            context={
                "stargazers_count": 0,
                "forks_count": 0,
            },
            source="source_1",
        ),
        # Additional IOL of repo 1
        PotentialLeakSource(
            url="url_repo_1",
            name="name_iol_2",
            html_url="html_url_iol_2",
            last_modified="Sat, 19 Dec 2022 15:34:56 UTC",
            content="content_iol_2",
            context={
                "stargazers_count": 1,
                "forks_count": 1,
            },
            source="source_1",
        ),
        # Additional IOL in another repo (2).
        PotentialLeakSource(
            url="url_repo_2",
            name="name_iol_3",
            html_url="html_url_iol_2",
            last_modified="Sat, 19 Dec 2022 15:34:56 UTC",
            content="content_iol_3",
            context={
                "stargazers_count": 0,
                "forks_count": 0,
            },
            source="source_2",
        ),
    ]
