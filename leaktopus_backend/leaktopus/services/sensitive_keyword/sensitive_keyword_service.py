from leaktopus.services.sensitive_keyword.provider_interface import SensitiveKeywordProviderInterface


class SensitiveKeywordException(Exception):
    pass


class SensitiveKeywordService:
    def __init__(self, sensitive_keyword_provider: SensitiveKeywordProviderInterface):
        self.sensitive_keyword_provider = sensitive_keyword_provider

    def get_sensitive_keywords(self, **kwargs):
        return self.sensitive_keyword_provider.get_sensitive_keywords(**kwargs)

    def add_sensitive_keyword(self, leak_id, keyword, url, **kwargs):
        return self.sensitive_keyword_provider.add_sensitive_keyword(leak_id, keyword, url, **kwargs)
