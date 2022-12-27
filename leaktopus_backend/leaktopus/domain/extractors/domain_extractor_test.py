from .domain_extractor import DomainExtractor


def test_should_extract_domains_successfully():
    content = "blah blah blah test.com test2.com blahlbalhlahlah"
    domain_extractor = DomainExtractor(tlds=["com", "org"])
    domains = domain_extractor.extract(content)
    assert domains == ["test.com", "test2.com"]
