import os
import shutil
from git.repo.base import Repo
import subprocess
from loguru import logger

from leaktopus.app import create_celery_app

celery = create_celery_app()
# How many times to retry the analysis task before failing.
ANALYSIS_MAX_RETRIES = 10
# Interval between analysis task retry.
RETRY_INTERVAL = 30
# Maximum size (in KB) of repository to clone. Reps bigger than that will be skipped.
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


def get_enhancement_modules():
    return [
        "domains",
        "sensitive_keywords",
        "contributors",
        "secrets"
    ]


@celery.task(bind=True, max_retries=ANALYSIS_MAX_RETRIES)
def enhance_repo(self, repo_name, organization_domains, sensitive_keywords, enhancement_modules):
    import datetime
    from leaktopus.common.secrets_scanner import scan as secrets_scan
    from leaktopus.common.domains_scanner import scan as domains_scan
    from leaktopus.common.contributors_extractor import scan as contributors_extractor
    from leaktopus.common.sensitive_keywords_extractor import scan as sensitive_keywords_extractor

    logger.info("Starting analysis of {}", repo_name)

    clones_base_dir = os.environ.get('CLONES_DIR', '/tmp/leaktopus-clones/')
    ts = datetime.datetime.now().timestamp()
    repo_path = "https://github.com/" + repo_name + ".git"
    clone_dir = os.path.join(clones_base_dir, str(ts), repo_name.replace("/", "_"))

    try:
        # Now, clone the repo.
        logger.debug("Cloning repository {} to {}", repo_path, clone_dir)
        Repo.clone_from(repo_path, clone_dir)

        # Prepare the full Git diff for secrets scan.
        logger.debug("Extracting Git diff for {}", repo_path)
        subprocess.call(['sh', '/app/secrets/git-extract-diff'], cwd=clone_dir)
        # Extract the commits history from the repository.
        full_diff_dir = os.path.join(clone_dir, 'commits_data')

        logger.debug("Starting the enrichment tasks for {}", repo_path)

        if "domains" in enhancement_modules:
            domains_scan(repo_path, full_diff_dir, organization_domains)

        if "sensitive_keywords" in enhancement_modules:
            sensitive_keywords_extractor(repo_path, full_diff_dir, sensitive_keywords)

        if "contributors" in enhancement_modules:
            contributors_extractor(repo_path, full_diff_dir, organization_domains)

        if "secrets" in enhancement_modules:
            secrets_scan(repo_path, full_diff_dir)
    except Exception as e:
        logger.error("Exception raised on the analysis of {}, it would be retried soon. Exception: {}", repo_name, e)

        # Cleanup of repo clone.
        shutil.rmtree(os.path.join(clones_base_dir, str(ts)), ignore_errors=True)
        logger.debug("Completed  the data cleanup for {} - {}", repo_name, clone_dir)

        raise self.retry(exc=e, countdown=RETRY_INTERVAL)

    # Cleanup of repo clone.
    shutil.rmtree(os.path.join(clones_base_dir, str(ts)), ignore_errors=True)
    logger.debug("Completed the data cleanup for {} - {}", repo_name, clone_dir)
    logger.info("Completed the analysis of {}", repo_name)


@celery.task(bind=True, max_retries=ANALYSIS_MAX_RETRIES)
def enhance_scanned_repo(self, repo_name, scan_id, organization_domains, sensitive_keywords, enhancement_modules):
    import leaktopus.common.scans as scans

    # Check if the scan should be aborted.
    if scans.is_scan_aborting(scan_id):
        logger.info("Aborting scan {}", scan_id)
        return True

    if is_repo_max_size_exceeded(repo_name):
        logger.info("Skipped {} since max size exceeded", repo_name)
        return True

    enhance_repo(repo_name, organization_domains, sensitive_keywords, enhancement_modules)


@celery.task
def leak_enhancer(repos_full_names, scan_id, organization_domains=[], sensitive_keywords=[], enhancement_modules=[]):
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

    # Skip the step if no enhancement modules were provided.
    if not enhancement_modules:
        logger.info('Skipped enhancement for scan #{} (no enhancement modules were provided).', scan_id)
        return repos_full_names

    enhance_tasks = []
    for repo_name in repos_full_names:
        # Create the group of enhancement tasks, one per repository.
        enhance_tasks.append(enhance_scanned_repo.s(
                repo_name=repo_name,
                scan_id=scan_id,
                organization_domains=organization_domains,
                sensitive_keywords=sensitive_keywords,
                enhancement_modules=enhancement_modules)
        )

    # Run the enhance in async
    task_group = group(enhance_tasks)
    result_group = task_group.apply_async()

    # Waiting for all analysis tasks to finish.
    while result_group.waiting():
        continue

    if result_group.successful():
        logger.info('Done analyzing leaks for scan #{}.', scan_id)
    else:
        logger.warning('There was an error in one of the enhancement tasks of scan #{}.', scan_id)

    return repos_full_names
