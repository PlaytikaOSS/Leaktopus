from celery import shared_task
import os
import time
from datetime import datetime
from github import Github, RateLimitExceededException
from leaktopus.common.elasticsearch_handler import es

# The Threshold should be higher from the number of worker threads.
GITHUB_RATE_LIMIT_THRESHOLD = 20
ES_INDEX_NAME = "leaktopus-gh-commits"


def publish_commits_to_github(commits):
    es.indices.create(index=ES_INDEX_NAME, ignore=400)
    for commit in commits:
        commit["timestamp"]: datetime.now()
        res = es.index(index=ES_INDEX_NAME, id=commit["sha"], body=commit)


def is_exceeding_gh_rate_limit(g):
    # Get commit without hitting GitHub's rate-limits.
    if g.rate_limiting[0] < GITHUB_RATE_LIMIT_THRESHOLD:
        rl_resettime = datetime.fromtimestamp(g.rate_limiting_resettime)
        seconds_till_rl_reset = (rl_resettime - datetime.now()).total_seconds()

        return seconds_till_rl_reset

    return False


def is_commit_indexed(sha):
    return es.exists(index=ES_INDEX_NAME, id=sha)


@shared_task()
def github_index_commits(repos_full_names, scan_id):
    import leaktopus.common.scans as scans
    from leaktopus.models.scan_status import ScanStatus

    # Skip step if abort was requested.
    if scans.is_scan_aborting(scan_id):
        return repos_full_names

    # Exit if repos_full_names is empty(failure in previous steps).
    if not repos_full_names:
        return []

    # Check whether commits index is enabled and functional, otherwise skip this method.
    is_es_enabled = os.getenv("ES_INDEXING_ENABLED", 'True').lower() in ['true', '1']
    if not is_es_enabled or not es.ping():
        return repos_full_names

    # Update the status, since aborting wasn't requested.
    scans.update_scan_status(scan_id, ScanStatus.SCAN_INDEXING)

    github_access_token = os.environ.get('GITHUB_ACCESS_TOKEN')

    for repo_full_name in repos_full_names:
        commits_struct = []

        try:
            g = Github(github_access_token)
            rl_reset = is_exceeding_gh_rate_limit(g)

            repo = g.get_repo(repo_full_name)
            commits = repo.get_commits()
            for commit in commits:
                sha = commit.sha
                if is_commit_indexed(sha):
                    # Skip commits that are already indexed.
                    continue

                # If approaching GitHub's rate-limit, create a new task that will start after reset
                if rl_reset:
                    github_index_commits.apply_async(args=[repo_full_name], countdown=rl_reset)
                    continue

                commit_ext = repo.get_commit(sha)

                struct = {
                    "repo_full_name": repo_full_name,
                    "commit_author": commit_ext.commit.author.name,
                    "html_url": commit_ext.html_url,
                    "sha": sha,
                    "last_modified": commit_ext.last_modified
                }

                for i in range(len(commit_ext.files)):
                    file = commit_ext.files[i]
                    if file.patch:
                        struct["patch-" + str(i)] = file.patch

                commits_struct.append(struct)

        except RateLimitExceededException:
            # In case we still hit the limit - add this task again.
            github_index_commits.apply_async(args=[repo_full_name], countdown=rl_reset)
            # print('GitHub rate limit exceeded.')

        publish_commits_to_github(commits_struct)

    return repos_full_names
