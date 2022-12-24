import pytest

from leaktopus.services.ignore_pattern.ignore_pattern_provider_interface import (
    IgnorePatternProviderInterface,
)
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.provider_interface import LeakProviderInterface
from leaktopus.usecases.scan.email_extractor import EmailExtractor
from leaktopus.usecases.scan.potential_leak_source import PotentialLeakSource
from leaktopus.usecases.scan.potential_leak_source_filter_interface import (
    PotentialLeakSourceFilterInterface,
)
from leaktopus.usecases.scan.save_potential_leak_source_page_use_case import (
    SavePotentialLeakSourcePageUseCase,
)


def test_should_save_potential_leak_source_page_successfully(
    leak_provider_mock,
    ignore_pattern_provider_mock,
    potential_leak_source_filter_mock,
    page_results,
):
    search_query = "test"
    scan_id = 1

    leak_provider_mock.add_leak.return_value = None
    ignore_pattern_provider_mock.get_ignore_patterns.return_value = []
    potential_leak_source_filter_mock.filter.return_value = True

    leak_service = LeakService(leak_provider=leak_provider_mock)
    use_case = SavePotentialLeakSourcePageUseCase(
        leak_service=leak_service,
        potential_leak_source_filter=potential_leak_source_filter_mock,
        email_extractor=EmailExtractor(organization_domains=["test.com", "test2.com"]),
    )
    use_case.execute(scan_id, page_results, search_query)
    leak_provider_mock.add_leak.assert_called()


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
            url="url_1",
            name="name_1",
            html_url="html_url_1",
            last_modified="Sat, 19 Dec 2022 15:34:56 UTC",
            content="contnet_1",
            repo_name="repo_name_1",
            repo_description="repo_description_1",
            context={
                "file_name": "file_name_1",
            },
            source="source_1",
        ),
        PotentialLeakSource(
            url="url_1",
            name="name_1",
            html_url="html_url_1",
            last_modified="Sat, 19 Dec 2022 15:34:56 UTC",
            content="contnet_1",
            repo_name="repo_name_1",
            repo_description="repo_description_1",
            context={
                "file_name": "file_name_1",
            },
            source="source_1",
        ),
        PotentialLeakSource(
            url="url_2",
            name="name_2",
            html_url="html_url_2",
            last_modified="Sat, 19 Dec 2022 15:34:56 UTC",
            content="contnet_2",
            repo_name="repo_name_2",
            repo_description="repo_description_2",
            context={
                "file_name": "file_name_2",
            },
            source="source_2",
        ),
    ]
