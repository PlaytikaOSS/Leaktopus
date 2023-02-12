import pytest
from copy import copy

from leaktopus.details.scan.potential_leak_source_request import PotentialLeakSourceRequest
from leaktopus.domain.enhancements.usecases.enhance_potential_leak_source_use_case import \
    EnhancePotentialLeakSourceUseCase
from leaktopus.services.enhancement_module.enhancement_module_provider import EnhancementModuleProviderInterface
from leaktopus.services.enhancement_status.provider_interface import EnhancementStatusProviderInterface
from leaktopus.services.leak.leak import Leak
from leaktopus.services.leak.provider_interface import LeakProviderInterface


def assert_enhancement_status_updated_when_pls_modified(
        use_case: EnhancePotentialLeakSourceUseCase,
        potential_leak_source_request: PotentialLeakSourceRequest,
        leak_service: LeakProviderInterface,
        enhancement_status_service: EnhancementStatusProviderInterface,
        base_leaks,
        full_diff_dir
):
    new_last_modified = "1675019000"
    leak_service.update_leak(base_leaks[0].leak_id, last_modified=new_last_modified)
    results = use_case.execute(potential_leak_source_request, base_leaks[0].url, full_diff_dir)
    assert len(results) == 1

    es = enhancement_status_service.get_enhancement_status(id=results[0])
    assert es[0].last_modified == new_last_modified



def assert_enhancement_skipped_when_pls_unmodified(
        use_case: EnhancePotentialLeakSourceUseCase,
        potential_leak_source_request: PotentialLeakSourceRequest,
        url,
        full_diff_dir
    ):
    results = use_case.execute(potential_leak_source_request, url, full_diff_dir)
    assert len(results) == 0


def test_should_enhance_potential_leak_sources_successfully(
        factory_leak_service: LeakProviderInterface,
        factory_enhancement_status_service: EnhancementStatusProviderInterface,
        factory_enhancement_module_service: EnhancementModuleProviderInterface,
        potential_leak_source_request: PotentialLeakSourceRequest,
        base_leaks,
        full_diff_dir
):
    leak_service = factory_leak_service(base_leaks)
    enhancement_status_service = factory_enhancement_status_service()
    use_case = EnhancePotentialLeakSourceUseCase(
        leak_service=leak_service,
        enhancement_status_service=enhancement_status_service,
        enhancement_module_services=factory_enhancement_module_service()
    )

    results = use_case.execute(potential_leak_source_request, base_leaks[0].url, full_diff_dir)
    assert len(results) == 1

    assert_enhancement_status_updated_when_pls_modified(use_case, potential_leak_source_request, leak_service, enhancement_status_service, base_leaks, full_diff_dir)
    assert_enhancement_skipped_when_pls_unmodified(use_case, potential_leak_source_request, base_leaks[0].url, full_diff_dir)


def test_should_skip_acknowledged_enhance_potential_leak_sources_successfully(
        factory_leak_service,
        factory_enhancement_status_service,
        factory_enhancement_module_service,
        potential_leak_source_request,
        base_leaks,
        full_diff_dir
):
    # Mark as acknowledged.
    base_leaks[0].acknowledged = True

    use_case = EnhancePotentialLeakSourceUseCase(
        leak_service=factory_leak_service(base_leaks),
        enhancement_status_service=factory_enhancement_status_service(),
        enhancement_module_services=factory_enhancement_module_service()
    )

    results = use_case.execute(potential_leak_source_request, base_leaks[0].url, full_diff_dir)
    assert len(results) == 0


def test_enhance_should_support_multiple_pls_search_queries(
        factory_leak_service,
        factory_enhancement_status_service,
        factory_enhancement_module_service,
        potential_leak_source_request,
        base_leaks,
        full_diff_dir
):
    leaks = base_leaks + [
        Leak(
            2,
            "https://github.com/foo/bar",
            "search_query_2",
            "github",
            {},
            [],
            False,
            "1675104599",
            "1675111799",
    )]

    enhancement_status_service = factory_enhancement_status_service()
    use_case = EnhancePotentialLeakSourceUseCase(
        leak_service=factory_leak_service(leaks),
        enhancement_status_service=enhancement_status_service,
        enhancement_module_services=factory_enhancement_module_service()
    )

    results_1 = use_case.execute(potential_leak_source_request, leaks[0].url, full_diff_dir)
    assert results_1[0] == 1

    potential_leak_source_request_2 = copy(potential_leak_source_request)
    potential_leak_source_request_2.search_query="search_query_2"
    results_2 = use_case.execute(potential_leak_source_request_2, leaks[0].url, full_diff_dir)
    assert results_2[0] == 2

    es = enhancement_status_service.get_enhancement_status()
    assert len(es) == 2


@pytest.fixture
def full_diff_dir():
    return "full_diff_dir"


@pytest.fixture
def base_leaks() -> list[Leak]:
    leak_id = 1
    url = "https://github.com/foo/bar"
    search_query = "search_query"
    leak_type = "github"
    context = {}
    iols = []
    acknowledged = False
    last_modified = "1675018199"
    created_at = "1675025399"

    return [
        Leak(leak_id, url, search_query, leak_type, context, iols, acknowledged, last_modified, created_at)
    ]


@pytest.fixture
def potential_leak_source_request():
    return PotentialLeakSourceRequest(
        scan_id=1,
        search_query="search_query",
        organization_domains=[],
        sensitive_keywords=[],
        enhancement_modules=[],
        provider_type=[]
    )
