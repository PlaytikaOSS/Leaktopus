from dataclasses import dataclass


@dataclass
class PotentialLeakSourceRequest:
    scan_id: int
    search_query: str
    organization_domains: list
    sensitive_keywords: list
    enhancement_modules: list
