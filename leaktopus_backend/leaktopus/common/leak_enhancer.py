import os
import datetime
import shutil
from git.repo.base import Repo
import subprocess

from leaktopus.app import create_celery_app

celery = create_celery_app()


@celery.task
def leak_enhancer(repos_full_names, scan_id, organization_domains=[], sensitive_keywords=[]):
    from leaktopus.common.secrets_scanner import scan as secrets_scan
    from leaktopus.common.domains_scanner import scan as domains_scan
    from leaktopus.common.contributors_extractor import scan as contributors_extractor
    from leaktopus.common.sensitive_keywords_extractor import scan as sensitive_keywords_extractor

    # Skip step if abort was requested.
    import leaktopus.common.scans as scans
    from leaktopus.models.scan_status import ScanStatus
    if scans.is_scan_aborting(scan_id):
        return repos_full_names

    # Exit if repos_full_names is empty(failure in previous steps).
    if not repos_full_names:
        return []

    # Update the status, since aborting wasn't requested.
    scans.update_scan_status(scan_id, ScanStatus.SCAN_ANALYZING)

    clones_base_dir = os.environ.get('CLONES_DIR', '/tmp/leaktopus-clones/')
    ts = datetime.datetime.now().timestamp()

    for repo_name in repos_full_names:
        if scans.is_scan_aborting(scan_id):
            continue

        repo_path = "https://github.com/" + repo_name + ".git"
        clone_dir = os.path.join(clones_base_dir, str(ts), repo_name.replace("/", "_"))

        # Now, clone the repo.
        Repo.clone_from(repo_path, clone_dir)

        # Prepare the full Git diff for secrets scan.
        subprocess.call(['sh', '/app/secrets/git-extract-diff'], cwd=clone_dir)
        # Run the secrets scanning tool (shhgit)
        full_diff_dir = os.path.join(clone_dir, 'commits_data')

        domains_scan(repo_path, full_diff_dir, organization_domains)
        sensitive_keywords_extractor(repo_path, full_diff_dir, sensitive_keywords)
        contributors_extractor(repo_path, full_diff_dir, organization_domains)
        secrets_scan(repo_path, full_diff_dir)

        # Cleanup of repo clone.
        # @todo Cleanup even in case of an error.
        shutil.rmtree(clone_dir, ignore_errors=True)

    # Cleanup of entire analysis directory.
    shutil.rmtree(os.path.join(clones_base_dir, str(ts)), ignore_errors=True)

    return repos_full_names
