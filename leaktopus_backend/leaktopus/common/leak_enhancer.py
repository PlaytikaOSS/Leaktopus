import os
import shutil
from git.repo.base import Repo
import subprocess

from leaktopus.app import create_celery_app

celery = create_celery_app()
# How many times to retry the analysis task before failing.
ANALYSIS_MAX_RETRIES = 5
# Interval between analysis task retry.
RETRY_INTERVAL = 30
# Maximum size (in KB) of repository to clone. Reps bigger than that will be skipped.
# @todo Increase and allow to control via environment variable.
REPO_MAX_SIZE = os.environ.get('REPO_MAX_CLONE_SIZE', 100000)


def is_repo_max_size_exceeded(repo_name):
    import requests
    res = requests.get(f"https://api.github.com/repos/{repo_name}")
    if res.status_code == 200:
        repo_metadata = res.json()
        if "size" in repo_metadata:
            return int(repo_metadata["size"]) > int(REPO_MAX_SIZE)

    # Fallback to true so the repository won't be tested.
    return True


@celery.task(bind=True, max_retries=ANALYSIS_MAX_RETRIES)
def enhance_repo(self, repo_name, scan_id, clones_base_dir, organization_domains, sensitive_keywords):
    import datetime
    import leaktopus.common.scans as scans
    from leaktopus.common.secrets_scanner import scan as secrets_scan
    from leaktopus.common.domains_scanner import scan as domains_scan
    from leaktopus.common.contributors_extractor import scan as contributors_extractor
    from leaktopus.common.sensitive_keywords_extractor import scan as sensitive_keywords_extractor

    if scans.is_scan_aborting(scan_id):
        return True

    if is_repo_max_size_exceeded(repo_name):
        print(f"Skipped {repo_name} since max size exceeded")
        return True

    ts = datetime.datetime.now().timestamp()
    repo_path = "https://github.com/" + repo_name + ".git"
    clone_dir = os.path.join(clones_base_dir, str(ts), repo_name.replace("/", "_"))

    try:
        # Now, clone the repo.
        Repo.clone_from(repo_path, clone_dir)

        # Prepare the full Git diff for secrets scan.
        subprocess.call(['sh', '/app/secrets/git-extract-diff'], cwd=clone_dir)
        # Extract the commits history from the repository.
        full_diff_dir = os.path.join(clone_dir, 'commits_data')

        domains_scan(repo_path, full_diff_dir, organization_domains)
        sensitive_keywords_extractor(repo_path, full_diff_dir, sensitive_keywords)
        contributors_extractor(repo_path, full_diff_dir, organization_domains)
        secrets_scan(repo_path, full_diff_dir)
    except Exception as e:
        print(f'Exception raised on the analysis of {repo_name}, it would be retried soon.')

        # Cleanup of repo clone.
        shutil.rmtree(os.path.join(clones_base_dir, str(ts)), ignore_errors=True)

        raise self.retry(exc=e, countdown=RETRY_INTERVAL)

    # Cleanup of repo clone.
    shutil.rmtree(os.path.join(clones_base_dir, str(ts)), ignore_errors=True)


@celery.task
def leak_enhancer(repos_full_names, scan_id, organization_domains=[], sensitive_keywords=[]):
    from celery import group
    import leaktopus.common.scans as scans
    from leaktopus.models.scan_status import ScanStatus

    # Skip step if abort was requested.
    if scans.is_scan_aborting(scan_id):
        return repos_full_names

    # Exit if repos_full_names is empty(failure in previous steps).
    if not repos_full_names:
        return []

    # Update the status, since aborting wasn't requested.
    scans.update_scan_status(scan_id, ScanStatus.SCAN_ANALYZING)

    clones_base_dir = os.environ.get('CLONES_DIR', '/tmp/leaktopus-clones/')

    enhance_tasks = []
    for repo_name in repos_full_names:
        # Create the group of enhancement tasks, one per repository.
        enhance_tasks.append(enhance_repo.s(
                repo_name=repo_name,
                scan_id=scan_id,
                clones_base_dir=clones_base_dir,
                organization_domains=organization_domains,
                sensitive_keywords=sensitive_keywords)
        )

    # Run the enhance in async
    task_group = group(enhance_tasks)
    result_group = task_group.apply_async()

    # Waiting for all analysis tasks to finish.
    while result_group.waiting():
        continue

    if result_group.successful():
        print('Done analyzing leaks.')
    else:
        print('Error in one of the enhancement tasks.')

    return repos_full_names
