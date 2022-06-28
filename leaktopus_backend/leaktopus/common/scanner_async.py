import os
from github import Github, RateLimitExceededException, BadCredentialsException, GithubException
from datetime import datetime
import re
import json
import leaktopus.common.db_handler as dbh
from leaktopus.app import create_celery_app

celery = create_celery_app()

# Filters definitions
# @todo Migrate to a configuration table.
MIN_FORKS_FILTER = 2
MAX_STARS_FILTER = 2
MIN_NON_ORG_EMAIL = 5
MIN_DOMAINS_NUMBER = 150


def github_datetime_to_timestamp(github_datetime):
    last_modified_datetime = datetime.strptime(github_datetime, '%a, %d %b %Y %H:%M:%S %Z')
    return datetime.timestamp(last_modified_datetime)


def save_gh_leaks(code_results, search_query, organization_domains):
    import leaktopus.common.db_handler as dbh

    if not code_results:
        return []

    # Gather leaks.
    grouped_results = []
    for res in code_results:
        clone_url = res.repository.clone_url

        leak_data = {
            "file_name": res.name,
            "file_url": res.html_url,
            "org_emails": get_org_emails(res.decoded_content.decode(), organization_domains)
        }

        # Group by repos.
        if any(d['url'] == clone_url for d in grouped_results):
            existing_res_key = next((i for i, item in enumerate(grouped_results) if item["url"] == clone_url), None)
            grouped_results[existing_res_key]["leaks"].append(leak_data)
        else:
            grouped_results.append({
                "url": clone_url,
                "last_modified": github_datetime_to_timestamp(res.repository.last_modified),
                "leaks": [leak_data],
                "search_query": search_query,
                "type": "github",
                "context": {
                    "repo_name": res.repository.name,
                    "owner": res.repository.owner.login if res.repository.owner.login else False,
                    # "organization": res.repository.organization if res.repository.organization else False,
                    "repo_description": res.repository.description,
                    "default_branch": res.repository.default_branch,
                    "is_fork": res.repository.fork,
                    "forks_count": res.repository.forks_count,
                    "watchers_count": res.repository.watchers_count,
                    "stargazers_count": res.repository.stargazers_count,
                    # The commit sha it was found on.
                    # "sha": res.sha
                }
            })

    # Now, save all the (grouped) leaks to the DB.
    for leaks_repo in grouped_results:
        # Skip if existing and if not modified since acknowledged.
        existing_leak = get_leak(clone_url)
        # @todo Update leak in case that the repo was modified since previous scan and it wasn't acknowledged yet.
        if existing_leak and not existing_leak["acknowledged"]:
            continue

        dbh.add_leak(
            leaks_repo["url"],
            search_query,
            "github",
            json.dumps(leaks_repo["context"]),
            json.dumps(leaks_repo["leaks"]),
            False,
            leaks_repo["last_modified"]
        )

    return grouped_results


def github_authenticate():
    # Authenticate to github
    github_access_token = os.environ.get('GITHUB_ACCESS_TOKEN')
    if not github_access_token:
        print("Error: GitHub API key is missing.")
        return None
    try:
        g = Github(github_access_token)
    except BadCredentialsException:
        print('Error:GitHub bad credentials.')
        return None
    except RateLimitExceededException as e:
        raise
    return g


def github_get_pages_object(g, search_query):
    # Get Pygithub object of code_results
    try:
        # search_base_filter = f' stars:<{MAX_STARS_FILTER}'
        # code_results = g.search_code(query=(search_query + search_base_filter))
        code_results = g.search_code(query=search_query)
        total_count = code_results.totalCount
    except RateLimitExceededException:
        raise
    if not isinstance(total_count, int):
        return None
    if total_count == 0:
        return None

    return code_results


def github_get_num_of_pages(results):
    # Get number of pages the code_search object has
    from urllib.parse import urlparse
    from urllib.parse import parse_qs

    try:
        url = results._getLastPageUrl()
    except RateLimitExceededException as e:
        raise
    except Exception as e:
        print("error with getting last page url")
        return None
    if url:
        num_of_pages = int(parse_qs(urlparse(url).query)['page'][0])
    else:
        num_of_pages = 1

    return num_of_pages


@celery.task(bind=True, max_retries=200)
def github_preprocessor(self, search_query, scan_id):
    from leaktopus.exceptions.scans import ScanHasNoResults

    # Authenticates to github, get results object, get number of pages the object has
    try:
        g = github_authenticate()
        if not g:
            return None

        results = github_get_pages_object(g, search_query)
        if not results or results.totalCount == 0:
            raise ScanHasNoResults("")

        num_pages = github_get_num_of_pages(results)
        if not num_pages:
            return None

    except RateLimitExceededException as e:
        print(f'exception raised on preprocessing github, it would be retry after 5 seconds')
        raise self.retry(exc=e, countdown=5)

    answer = {"results": results, "num_pages": num_pages, "search_query": search_query}
    return answer


def merge_pages(pages):
    # Takes list of pages and returns lists of results
    results = []
    for page in pages:
        # Support case where page is None (e.g., scan aborted).
        if not page:
            return results

        results.extend(page)
    return results


@celery.task()
def github_fetch_pages(struct, scan_id, organization_domains):
    # Executing tasks to get results per page
    from celery import group
    from celery.result import allow_join_result

    # Error or no results
    if not struct:
        return []

    # Skip step if abort was requested.
    import leaktopus.common.scans as scans
    from leaktopus.models.scan_status import ScanStatus
    if scans.is_scan_aborting(scan_id):
        return []

    # group of tasks, one per page
    task_group = group([
        github_get_page.s(results=struct["results"], page_num=n, scan_id=scan_id) for n in range(struct["num_pages"])
    ])
    result_group = task_group.apply_async()

    # Waiting for all pages to finish
    while result_group.waiting():
        continue

    # Celery flag to allow join
    with allow_join_result():
        if result_group.successful():
            # Gather results to list
            results_group_list = result_group.join()
            merged_pages = merge_pages(results_group_list)
            gh_results_filtered = filter_gh_results(merged_pages, organization_domains)
            return save_gh_leaks(gh_results_filtered, struct["search_query"], organization_domains)
        else:
            print('Error: One of the pages tasks were unsuccessful')
            return []


@celery.task(bind=True, max_retries=200)
def github_get_page(self, results, page_num, scan_id):
    # Skip step if abort was requested.
    import leaktopus.common.scans as scans
    from leaktopus.models.scan_status import ScanStatus
    if scans.is_scan_aborting(scan_id):
        return None

    # Get results of a specific page
    try:
        cur_page = results.get_page(page_num)
        # Force download attributes.
        # @todo get rid of this code
        for result in cur_page:
            try:
                clone_url = result.repository.clone_url
                forks_count = result.repository.forks_count
                stargazers = result.repository.stargazers_count
                content = result.decoded_content.decode()
                last_modified = result.repository.last_modified
                repo_name = result.repository.name
                owner = result.repository.owner.login
                desc = result.repository.description
                default_branch = result.repository.default_branch
                fork = result.repository.fork
                watchers_count = result.repository.watchers_count
            except GithubException as e:
                if "404" in str(e.__str__):
                    continue
                else:
                    raise RateLimitExceededException
            except TimeoutError as e:
                continue
    except RateLimitExceededException as e:
        print(f'Exception raised on getting page number {page_num} github, it would be retried after 10 seconds')
        raise self.retry(exc=e, countdown=10)
    return cur_page


@celery.task()
def gh_get_repos_full_names(gh_results_struct):
    repo_full_names = []

    # Exit if gh_results_struct is empty(failure in previous steps).
    if not gh_results_struct:
        return []

    for result in gh_results_struct:
        repo_full_names.append(result["context"]["owner"] + "/" + result["context"]["repo_name"])

    return repo_full_names


@celery.task
def update_scan_status_async(repos_full_names, scan_id):
    import leaktopus.common.scans as scans
    from leaktopus.models.scan_status import ScanStatus
    if scans.is_scan_aborting(scan_id):
        # Set the status to aborted (this is the last step).
        scans.update_scan_status(scan_id, ScanStatus.SCAN_ABORTED)
        return True

    # Update the scan status.
    if repos_full_names:
        scans.update_scan_status(scan_id, ScanStatus.SCAN_DONE)
    else:
        scans.update_scan_status(scan_id, ScanStatus.SCAN_FAILED)


@celery.task
def error_handler(request, exc, traceback, scan_id):
    from leaktopus.exceptions.scans import ScanHasNoResults

    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          request.id, exc, traceback))

    import leaktopus.common.scans as scans
    from leaktopus.models.scan_status import ScanStatus
    if isinstance(exc, ScanHasNoResults):
        # In case of no results exception - change the status to done.
        scans.update_scan_status(scan_id, ScanStatus.SCAN_DONE)
    else:
        scans.update_scan_status(scan_id, ScanStatus.SCAN_FAILED)


def scan(search_query, organization_domains=[], sensitive_keywords=[]):
    from leaktopus.common.github_indexer import github_index_commits
    from leaktopus.common.leak_enhancer import leak_enhancer
    import leaktopus.common.scans as scans

    # Do not run scan if one for the same search query is already running.
    running_scans = scans.get_running_scan_by_search_query(search_query)
    if running_scans:
        return running_scans[0]["scan_id"]

    # Add the scan to DB.
    scan_id = scans.add_scan(search_query)

    chain = github_preprocessor.s(search_query=search_query, scan_id=scan_id) |\
        github_fetch_pages.s(scan_id=scan_id, organization_domains=organization_domains) |\
        gh_get_repos_full_names.s() |\
        leak_enhancer.s(
            scan_id=scan_id,
            organization_domains=organization_domains,
            sensitive_keywords=sensitive_keywords
        ) |\
        github_index_commits.s(scan_id=scan_id) |\
        update_scan_status_async.s(scan_id=scan_id)
    chain.apply_async(link_error=error_handler.s(scan_id=scan_id))

    return scan_id


def get_emails_from_content(content):
    return re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)


def get_org_emails(content, organization_domains):
    org_emails = set()

    emails = get_emails_from_content(content)
    for email in emails:
        if email.split("@")[1] in organization_domains:
            org_emails.add(email)

    return list(org_emails)


def non_org_emails_count(content, organization_domains):
    count = 0
    # Find all emails in the content.
    emails = get_emails_from_content(content)
    for email in emails:
        if email.split("@")[1] not in organization_domains:
            count += 1

    return count


def domains_count(content):
    # Find all domains (common extensions only) in the content.
    # @todo Improve the extensions list.
    domains = re.findall(r'[\w\.-]+\.(?:com|net|info|io)', content, re.MULTILINE)

    return len(domains)


def is_ignored_repo(repo_url):
    # @todo Cache it in a smart way not to call the DB for each row.
    ignored_patterns = dbh.get_config_github_ignored()
    if not ignored_patterns:
        return False

    for pattern in ignored_patterns:
        if re.search(rf"{pattern['pattern']}", repo_url):
            return True

    return False


def get_leak(leak_url):
    known_leaks = dbh.get_leak(url=leak_url)

    if not known_leaks:
        # New leak.
        return False

    # Get the latest leak (sorted by created_at).
    return known_leaks[0]


def is_repo_requires_scan(repo):
    # Get the last known leak of the given repository.
    last_known_leak = get_leak(repo.repository.clone_url)

    # An existing leak.
    if not last_known_leak:
        return True

    # Check if the repository was modified since the previous scan.
    known_last_modified = last_known_leak["last_modified"]
    last_modified = github_datetime_to_timestamp(repo.repository.last_modified)
    if last_modified > known_last_modified:
        return True

    return False


def filter_gh_results(code_results, organization_domains):
    filtered_results = []

    # Replace with a dynamic list editable by the user.
    # gh_filtered_repos()
    for result in code_results:
        # Filter` repos with specific Regex.
        if is_ignored_repo(result.repository.clone_url):
            # print('ignored repo')
            continue

        if not is_repo_requires_scan(result):
            # print('not requires scan')
            continue

        # Do not add if it has more than 2 forks.
        if result.repository.forks_count >= MIN_FORKS_FILTER:
            # print('Too many forks')
            continue

        # Do not add if it has more than 2 stars.
        # @todo Replace by :stars<2 in the search query.
        if result.repository.stargazers_count >= MAX_STARS_FILTER:
            # print('Too many stars')
            continue

        content = result.decoded_content.decode()

        # Filter repos with a large number of non-organization email addresses.
        if non_org_emails_count(content, organization_domains) >= MIN_NON_ORG_EMAIL:
            # print('Many non org emails')
            continue

        # Ignore repos with a large number of domains in a list.
        if domains_count(content) >= MIN_DOMAINS_NUMBER:
            # print('Many domains in one place.')
            continue

        filtered_results.append(result)

    # In case that all results were filtered - raise no results exception.
    if not filtered_results:
        from leaktopus.exceptions.scans import ScanHasNoResults
        raise ScanHasNoResults("All results were filtered")

    return filtered_results
