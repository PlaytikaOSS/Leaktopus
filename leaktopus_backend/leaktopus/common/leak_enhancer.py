from celery import shared_task
import os
import shutil
from git.repo.base import Repo
import subprocess
from leaktopus.utils.common_imports import logger
import datetime
import requests

from leaktopus.domain.enhancements.usecases.enhance_potential_leak_source_use_case import \
    EnhancePotentialLeakSourceUseCase
from leaktopus.factory import create_leak_service, create_enhancement_status_service, create_enhancement_module_services

# How many times to retry the analysis task before failing.
ANALYSIS_MAX_RETRIES = 10
# Interval between analysis task retry.
RETRY_INTERVAL = 30
# Maximum size (in KB) of repository to clone. Reps bigger than that will be skipped.
REPO_MAX_SIZE = os.environ.get('REPO_MAX_CLONE_SIZE', 100000)


def is_github_repo_max_size_exceeded(repo_name):
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


def get_repo_full_path(repo_name, provider):
    if provider == "github":
        return "https://github.com/" + repo_name + ".git"


@shared_task(bind=True, max_retries=ANALYSIS_MAX_RETRIES)
def enhance_repo(self, repo_name, organization_domains, sensitive_keywords, enhancement_modules, **kwargs):
    logger.info("Starting analysis of {}", repo_name)

    clones_base_dir = os.environ.get('CLONES_DIR', '/tmp/leaktopus-clones/')
    ts = datetime.datetime.now().timestamp()
    repo_path = get_repo_full_path(repo_name, "github")
    clone_dir = os.path.join(clones_base_dir, str(ts), repo_name.replace("/", "_"))

    try:
        # @TODO Move the clone to within the enhancement modules with LeakSourceFetcher service.
        # Now, clone the repo.
        logger.debug("Cloning repository {} to {}", repo_path, clone_dir)
        Repo.clone_from(repo_path, clone_dir)

        # Prepare the full Git diff for secrets scan.
        logger.debug("Extracting Git diff for {}", repo_path)
        subprocess.call(['sh', '/app/secrets/git-extract-diff'], cwd=clone_dir)
        # Extract the commits history from the repository.
        full_diff_dir = os.path.join(clone_dir, 'commits_data')

        logger.debug("Starting the enrichment tasks for {}", repo_path)

        # Run the enhancement modules.
        potential_leak_source_request = kwargs.get('potential_leak_source_request', None)
        leak_service = create_leak_service()
        enhancement_status_service = create_enhancement_status_service()
        use_case = EnhancePotentialLeakSourceUseCase(
            leak_service=leak_service,
            enhancement_status_service=enhancement_status_service,
            enhancement_module_services=create_enhancement_module_services(enhancement_modules)
        )

        results = use_case.execute(potential_leak_source_request, repo_path, full_diff_dir)
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


@shared_task(bind=True, max_retries=ANALYSIS_MAX_RETRIES)
def enhance_scanned_repo(self, repo_name, scan_id, organization_domains, sensitive_keywords, enhancement_modules, **kwargs):
    import leaktopus.common.scans as scans

    # Check if the scan should be aborted.
    if scans.is_scan_aborting(scan_id):
        logger.info("Aborting scan {}", scan_id)
        return True

    if is_github_repo_max_size_exceeded(repo_name):
        logger.info("Skipped {} since max size exceeded", repo_name)
        return True

    enhance_repo(repo_name, organization_domains, sensitive_keywords, enhancement_modules, **kwargs)


@shared_task()
def leak_enhancer(repos_full_names, scan_id, organization_domains=[], sensitive_keywords=[], enhancement_modules=[], **kwargs):
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
                enhancement_modules=enhancement_modules,
                **kwargs
        ))

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
