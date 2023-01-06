import pytest

from leaktopus.domain.extractors.email_extractor import EmailExtractor


def test_should_extract_emails_with_success(email_extractor):
    # Test that no emails are extracted from a string without emails
    assert email_extractor.extract_emails_from_content("This is a string with no emails") == []

    # Test that all emails are extracted from a string with multiple emails
    assert email_extractor.extract_emails_from_content("This is a string with multiple emails: test1@test.com and test2@test.com \n new line should also work test@test3.co.uk") == ['test1@test.com', 'test2@test.com', 'test@test3.co.uk']


def test_should_extract_organization_emails_with_success(email_extractor):
    assert email_extractor.extract_organization_emails("This is a string with multiple emails: test1@test.com and test2@foobar.com \n new line should also work test@test3.co.uk") == ['test1@test.com', 'test@test3.co.uk']


def test_should_extract_non_organization_emails_with_success(email_extractor):
    assert email_extractor.extract_non_organization_emails("This is a string with multiple emails: test1@test.com and test2@foobar.com \n new line should also work test@test3.co.uk \n baz@foo.com") == ['test2@foobar.com', 'baz@foo.com']


@pytest.fixture
def email_extractor():
    return EmailExtractor(organization_domains=["test.com", "test2.com", "test3.co.uk"])
