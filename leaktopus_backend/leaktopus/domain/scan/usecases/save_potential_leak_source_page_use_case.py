import json
from typing import List

from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.potential_leak_source_scan_status.service import (
    PotentialLeakSourceScanStatusService,
)
from leaktopus.domain.extractors.email_extractor import EmailExtractor
from leaktopus.domain.scan.entities.potential_leak_source import PotentialLeakSource
from leaktopus.domain.scan.contracts.potential_leak_source_filter_interface import (
    PotentialLeakSourceFilterInterface,
)


class SavePotentialLeakSourcePageUseCase:
    def __init__(
        self,
        leak_service: LeakService,
        potential_leak_source_filter: PotentialLeakSourceFilterInterface,
        email_extractor: EmailExtractor,
        potential_leak_source_scan_status_service: PotentialLeakSourceScanStatusService,
    ):
        self.leak_service = leak_service
        self.potential_leak_source_filter = potential_leak_source_filter
        self.email_extractor = email_extractor
        self.potential_leak_source_scan_status_service = (
            potential_leak_source_scan_status_service
        )

    def execute(
        self,
        scan_id,
        page_results: List[PotentialLeakSource],
        search_query,
        current_page_number,
    ):
        self.guard_empty_page_results(page_results)
        filtered_results = self.filter_results(scan_id, page_results)
        grouped_results = self.group_results_before_save(filtered_results, search_query)
        self.save_results(grouped_results, search_query)
        self.potential_leak_source_scan_status_service.mark_as_analyzing(
            scan_id, current_page_number
        )
        return grouped_results

    def group_results_before_save(self, filtered_results, search_query):
        grouped_results = []
        for result in filtered_results:
            org_emails = self.email_extractor.extract_organization_emails(
                json.dumps(result.content)
            )
            leak_data = self.generate_leak_data(result, org_emails)
            is_url_exists = self.is_url_exists(grouped_results, result)
            grouped_results = self.append_or_update_group_result(
                grouped_results, is_url_exists, leak_data, search_query, result
            )
        return grouped_results

    def guard_empty_page_results(self, page_results):
        if not page_results:
            raise ValueError("Page results cannot be empty")

    def filter_results(self, scan_id, page_results):
        filtered_results = []
        for result in page_results:
            if self.potential_leak_source_filter.filter(scan_id, result):
                filtered_results.append(result)
        return filtered_results

    def generate_leak_data(self, potential_leak_source, org_emails):
        return {
            "file_name": potential_leak_source.name,
            "file_url": potential_leak_source.html_url,
            "org_emails": org_emails,
        }

    def is_url_exists(self, grouped_results, potential_leak_source):
        is_url_exists = False
        for gr in grouped_results:
            if gr["potential_source_page"].url == potential_leak_source.url:
                is_url_exists = True
                break
        return is_url_exists

    def append_or_update_group_result(
        self,
        grouped_results,
        is_url_exists,
        leak_data,
        search_query,
        potential_leak_source,
    ):
        if is_url_exists:
            existing_res_key = None
            for i, gr in enumerate(grouped_results):
                if gr["potential_source_page"].url == potential_leak_source.url:
                    existing_res_key = i

            grouped_results[existing_res_key]["leaks"].append(leak_data)
        else:
            grouped_results.append(
                self.generate_result(
                    grouped_results, potential_leak_source, search_query, leak_data
                )
            )
        return grouped_results

    def generate_result(self, grouped_results, search_result, search_query, leak_data):
        return {
            "potential_source_page": search_result,
            "leaks": [leak_data],
        }

    def save_results(self, grouped_results, search_query):
        for result in grouped_results:
            potential_source_page = result["potential_source_page"]
            existing_leak = self.leak_service.get_leaks(url=potential_source_page.url)
            # @todo Update leak in case that the repo was modified since previous scan and it wasn't acknowledged yet.
            if existing_leak and not existing_leak["acknowledged"]:
                continue

            self.leak_service.add_leak(
                potential_source_page.url,
                search_query,
                potential_source_page.source,
                json.dumps(potential_source_page.context),
                json.dumps(result["leaks"]),
                False,
                potential_source_page.last_modified,
            )
