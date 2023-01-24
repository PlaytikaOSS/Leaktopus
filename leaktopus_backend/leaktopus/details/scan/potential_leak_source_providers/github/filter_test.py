import pytest

from leaktopus.services.ignore_pattern.ignore_pattern_service import (
    IgnorePatternService,
)
from leaktopus.services.leak.leak import Leak
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.provider_interface import LeakProviderInterface
from leaktopus.services.leaktopus_config.leaktopus_config_service import (
    LeaktopusConfigService,
)
from leaktopus.services.leaktopus_config.initial_config_leaktopus_config_provider import (
    InitialConfigLeaktopusConfigProvider,
)
from leaktopus.details.scan.potential_leak_source_providers.github.filter import (
    GithubPotentialLeakSourceFilter,
)
from leaktopus.domain.scan.entities.potential_leak_source import PotentialLeakSource


@pytest.mark.parametrize(
    "potential_leak_source, expected_filtered",
    [
        (
            PotentialLeakSource(
                url="url_1",
                name="name_1",
                html_url="html_url_1",
                last_modified="Sat, 20 Dec 2022 15:34:56 UTC",
                content="content_1",
                context={
                    "stargazers_count": 1,
                    "forks_count": 1,
                },
                source="source_1",
            ),
            True,
        ),
        (
            PotentialLeakSource(
                url="url_1",
                name="name_1",
                html_url="html_url_1",
                last_modified="Sat, 20 Dec 2022 15:34:56 UTC",
                content="content_1",
                context={
                    "stargazers_count": 11,
                    "forks_count": 11,
                },
                source="source_1",
            ),
            False,
        ),
    ],
)
def test_should_filter_potential_leak_sources_successfully(
    potential_leak_source,
    expected_filtered,
    domain_extractor,
    email_extractor,
    ignore_pattern_provider_mock,
    leak_provider_mock,
):
    scan_id = 1
    leak_provider_mock.get_leaks.return_value = [
        Leak(
            1,
            "url_1",
            "search_term_1",
            "leak_type_1",
            "context_1",
            "leaks",
            1,
            "Sat, 19 Dec 2022 15:34:56 UTC",
            "Sat, 19 Dec 2022 15:34:56 UTC",
        )
    ]
    leak_service = LeakService(
        leak_provider=leak_provider_mock,
    )
    ignore_pattern_service = IgnorePatternService(
        provider=ignore_pattern_provider_mock,
    )
    leaktopus_config_service = LeaktopusConfigService(
        provider=InitialConfigLeaktopusConfigProvider(
            {
                "tlds": ["com", "org"],
                "max_fork_count": 10,
                "max_star_count": 10,
                "max_non_org_emails": 10,
                "max_domain_emails": 10,
            }
        )
    )
    potential_leak_source_filter = GithubPotentialLeakSourceFilter(
        leak_service=leak_service,
        ignore_pattern_service=ignore_pattern_service,
        domain_extractor=domain_extractor,
        email_extractor=email_extractor,
        leaktopus_config_service=leaktopus_config_service,
    )
    filtered = potential_leak_source_filter.filter(
        scan_id=scan_id, potential_leak_source=potential_leak_source
    )
    assert filtered is expected_filtered


@pytest.fixture
def leak_provider_mock(mocker):
    return mocker.patch.object(LeakProviderInterface, "get_leaks")
