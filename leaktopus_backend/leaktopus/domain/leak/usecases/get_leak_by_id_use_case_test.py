import pytest

from .get_leak_by_id_use_case import GetLeakByIdUseCase


def test_should_get_leak_by_id_successfully(
        add_leak,
        factory_leak_service,
        factory_domain_service,
        factory_secret_service,
        factory_contributor_service,
        factory_sensitive_keyword_service
):
    leak_service = factory_leak_service()
    leak_id = add_leak(leak_service)
    # Add another leak to make sure we're getting the right one.
    add_leak(leak_service)

    # Add secrets, domains, contributors and another one
    secret_service = factory_secret_service()
    secret_id = secret_service.add_secret(leak_id, "https://foo.bar", "AWS Access Key", "*****")

    domain_service = factory_domain_service()
    domain_id = domain_service.add_domain(leak_id, "https://foo.bar", "foo.bar")

    contributor_service = factory_contributor_service()
    contributor_id = contributor_service.add_contributor(leak_id, "Foo Bar", "foo@bar.com", "foo@bar.com", False)

    sensitive_keyword_service = factory_sensitive_keyword_service()
    sensitive_keyword_id = sensitive_keyword_service.add_sensitive_keyword(leak_id, "1234567890", "https://foo.bar")

    use_case = GetLeakByIdUseCase(
        leak_service,
        secret_service,
        domain_service,
        contributor_service,
        sensitive_keyword_service
    )
    result_leak = use_case.execute(leak_id)

    # Assert that we got the right leak.
    assert result_leak["leak_id"] == leak_id

    # Assert that the leak has its IOLs populated.
    assert type(result_leak["iol"]) is list and len(result_leak["iol"]) == 2

    # Assert that the leak has the right secrets, domains, contributors and sensitive keywords.
    assert len(result_leak["secrets"]) == 1
    assert len(result_leak["domains"]) == 1
    assert len(result_leak["contributors"]) == 1
    assert len(result_leak["sensitive_keywords"]) == 1
