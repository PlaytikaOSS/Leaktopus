from leaktopus.services.sensitive_keyword.sensitive_keyword import SensitiveKeyword
from leaktopus.services.sensitive_keyword.provider_interface import (
    SensitiveKeywordProviderInterface,
)
import datetime

class SensitiveKeywordMemoryProvider(SensitiveKeywordProviderInterface):
    def __init__(self, sensitive_keywords=[], override_methods={}):
        self.sensitive_keywords = sensitive_keywords
        self.override_methods = override_methods

    def get_sensitive_keywords(self, **kwargs) -> list[SensitiveKeyword]:
        filtered_sensitive_keywords = self.sensitive_keywords

        for prop, value in kwargs.items():
            filtered_sensitive_keywords = [
                s for s in filtered_sensitive_keywords
                if getattr(s, prop) == value
            ]

        return (
            self.override_methods["get_sensitive_keywords"]()
            if "get_sensitive_keywords" in self.override_methods
            else filtered_sensitive_keywords
        )

    def save_sensitive_keywords(self, sensitive_keywords):
        if "save_sensitive_keywords" in self.override_methods:
            return self.override_methods["save_sensitive_keywords"](sensitive_keywords)

        for sensitive_keyword in sensitive_keywords:
            self.add_sensitive_keyword(
                sensitive_keyword.leak_id,
                sensitive_keyword.keyword,
                sensitive_keyword.url,
                **sensitive_keyword
            )

    def add_sensitive_keyword(self, leak_id, keyword, url, **kwargs):
        pid = len(self.sensitive_keywords) + 1
        now = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        sensitive_keyword = SensitiveKeyword(pid, leak_id, keyword, url, created_at, **kwargs)

        self.sensitive_keywords.append(sensitive_keyword)
        return (
            self.override_methods["add_sensitive_keyword"]()
            if "add_sensitive_keyword" in self.override_methods
            else pid
        )
