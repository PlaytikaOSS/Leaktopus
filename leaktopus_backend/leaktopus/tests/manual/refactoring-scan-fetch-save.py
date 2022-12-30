import os

from github import Github

from leaktopus.app import create_celery_app
from leaktopus.common.scanner_async import github_get_num_of_pages
from leaktopus.details.entrypoints.scan.task import (
    trigger_pages_scan_task_entrypoint,
)
from leaktopus.details.scan.potential_leak_source_request import (
    PotentialLeakSourceRequest,
)


def main():
    g = Github(os.environ["GITHUB_TOKEN"])
    search_query = "leaktopus"
    code_results = g.search_code(query=search_query)
    num_pages = github_get_num_of_pages(code_results)
    celery = create_celery_app()

    scan_id = 1
    initial_search_metadata = {
        "results": code_results,
        "num_pages": num_pages,
        "search_query": search_query,
    }
    organization_domains = [
        "leaktopus.com",
        "leaktopus.io",
    ]
    results = []
    potential_leak_source_request = PotentialLeakSourceRequest(
        scan_id=scan_id,
        search_query=search_query,
        organization_domains=organization_domains,
        enhancement_modules=[],
        sensitive_keywords=[],
        provider_type="github",
    )
    task = trigger_pages_scan_task_entrypoint.s(
        initial_search_metadata, potential_leak_source_request, "celery"
    )
    result = task.delay()
    result.wait()
    print(result)


if __name__ == "__main__":
    main()
