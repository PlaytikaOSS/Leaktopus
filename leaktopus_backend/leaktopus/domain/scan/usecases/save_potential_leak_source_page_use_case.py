import json
from typing import List

from leaktopus.domain.leak.leak_operator import LeakOperator
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
        results_with_enriched_iols = self.enrich_iols_in_results_before_save(filtered_results, search_query)
        self.save_results(results_with_enriched_iols, search_query)
        self.potential_leak_source_scan_status_service.mark_as_analyzing(
            scan_id, current_page_number
        )
        return results_with_enriched_iols

    def enrich_iols_in_results_before_save(self, filtered_results, search_query):
        enrich_iol_results = []
        for result in filtered_results:
            # @todo Should we extract emails in this phase although we'll extract it in the analysis phase as well?
            org_emails = self.email_extractor.extract_organization_emails(
                json.dumps(result.content)
            )
            iols_data = self.generate_leak_data(result, org_emails)

            enrich_iol_results.append(
                self.generate_result(
                    result, iols_data
                )
            )
        return enrich_iol_results

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


    def generate_result(self, search_result, iols_data):

        return {
            "potential_source_page": search_result,
            "iol": [iols_data],
        }

    def get_non_acknowledged_leaks(self, leaks):
        non_acknowledged_leaks = []

        for leak in leaks:
            if not leak.acknowledged:
                non_acknowledged_leaks.append(leak)

        return non_acknowledged_leaks


    def save_results(self, results_with_enriched_iols, search_query):
        for result in results_with_enriched_iols:
            potential_source_page = result["potential_source_page"]
            existing_leaks = self.leak_service.get_leaks(url=potential_source_page.url, search_query=search_query)

            if len(existing_leaks) == 0:
                self.leak_service.add_leak(
                    potential_source_page.url,
                    search_query,
                    potential_source_page.source,
                    json.dumps(potential_source_page.context),
                    json.dumps(result["iol"]),
                    False,
                    potential_source_page.last_modified,
                )
                continue

            non_acknowledged_leaks = self.get_non_acknowledged_leaks(existing_leaks)
            if non_acknowledged_leaks:
                # Update leak IOLs and context.
                self.leak_service.update_leak(
                    non_acknowledged_leaks[0].leak_id,
                    # Is it correct to assume that there'll always be only one IOL per PLS result?
                    IOL=result["iol"][0],
                    context=potential_source_page.context,
                    last_modified=potential_source_page.last_modified,
                )
            else:
                last_modified_leak = LeakOperator.get_latest_last_modified_leak(existing_leaks)
                last_modified_leak_datetime = last_modified_leak.last_modified

                if last_modified_leak_datetime > potential_source_page.last_modified:
                    self.leak_service.add_leak(
                        potential_source_page.url,
                        search_query,
                        potential_source_page.source,
                        json.dumps(potential_source_page.context),
                        json.dumps(result["iol"]),
                        False,
                        potential_source_page.last_modified,
                    )
