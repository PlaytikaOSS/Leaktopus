import re
from abc import abstractmethod

from loguru import logger

from leaktopus.common.scanner_async import datetime_to_timestamp
from leaktopus.services.ignore_pattern.ignore_pattern_service import (
    IgnorePatternService,
)
from leaktopus.services.leak.leak import Leak
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leaktopus_config.leaktopus_config_service import LeaktopusConfigService
from leaktopus.usecases.scan.domain_extractor import DomainExtractor
from leaktopus.usecases.scan.email_extractor import EmailExtractor
from leaktopus.usecases.scan.potential_leak_source import PotentialLeakSource
from leaktopus.usecases.scan.potential_leak_source_filter_interface import (
    PotentialLeakSourceFilterInterface,
)


class AbstractPotentialLeakSourceFilter(PotentialLeakSourceFilterInterface):
    def __init__(
        self,
        leak_service: LeakService,
        ignore_pattern_service: IgnorePatternService,
        domain_extractor: DomainExtractor,
        email_extractor: EmailExtractor,
        leaktopus_config_service: LeaktopusConfigService,
    ):
        self.leak_service = leak_service
        self.ignore_pattern_service = ignore_pattern_service
        self.domain_extractor = domain_extractor
        self.email_extractor = email_extractor
        self.leaktopus_config_service = leaktopus_config_service

    def filter(self, scan_id, potential_leak_source: PotentialLeakSource):
        if self.is_ignored_repo(potential_leak_source.url):
            return False

        if not self.is_repo_requires_scan(potential_leak_source):
            return False

        if self.fork_count_is_too_high(potential_leak_source):
            return False

        if self.star_count_is_too_high(potential_leak_source):
            return False

        content = potential_leak_source.content
        if self.too_many_non_org_emails(content):
            return False

        if self.too_many_domain_emails(content):
            return False

        return True

    def is_ignored_repo(self, repo_url):
        ignored_patterns = self.ignore_pattern_service.get_ignore_patterns()
        if not ignored_patterns:
            return False

        for pattern in ignored_patterns:
            if re.search(rf"{pattern['pattern']}", repo_url):
                return True

        return False

    def is_repo_requires_scan(self, potential_leak_source):
        leaks = self.leak_service.get_leaks(url=potential_leak_source.url)
        if self.leak_not_scanned(leaks):
            return True

        if self.repository_was_updated_since_last_scan(potential_leak_source, leaks[0]):
            return True

        return False

    def leak_not_scanned(self, leaks):
        return not leaks

    def repository_was_updated_since_last_scan(self, potential_leak_source, leak: Leak):
        known_last_modified = leak.last_modified
        last_modified = potential_leak_source.last_modified
        return last_modified > known_last_modified


    @abstractmethod
    def extract_star_count(self, potential_leak_source):
        raise NotImplementedError

    @abstractmethod
    def extract_fork_count(self, potential_leak_source):
        raise NotImplementedError

    def fork_count_is_too_high(self, potential_leak_source):
        return self.extract_fork_count(potential_leak_source) >= self.leaktopus_config_service.get_max_fork_count()

    def star_count_is_too_high(self, potential_leak_source):
        return self.extract_star_count(potential_leak_source) >= self.leaktopus_config_service.get_max_star_count()

    def too_many_non_org_emails(self, content):
        emails = self.email_extractor.extract_non_organization_emails(content)
        return len(emails) >= self.leaktopus_config_service.get_max_non_org_emails()

    def too_many_domain_emails(self, content):
        domains = self.domain_extractor.extract(content)
        return len(domains) >= self.leaktopus_config_service.get_max_domain_emails()
