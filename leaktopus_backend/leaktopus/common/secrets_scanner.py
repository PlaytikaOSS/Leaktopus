import os
import datetime
import shutil
from git.repo.base import Repo
import subprocess
import csv
import json
from truffleHog import truffleHog
from leaktopus.common.db_handler import add_secret, get_secret
from leaktopus.common.leak_handler import get_leak_by_url

# Max secrets to store per URL
MAX_SECRETS_PER_URL = 30


def store_secrets(url, secrets):
    # Filter by unique secrets.
    secrets_unique = list({v['match_string']: v for v in secrets}.values())

    # Get leak id from DB.
    leak = get_leak_by_url(url)

    if not leak:
        return False

    for secret in secrets_unique[0:MAX_SECRETS_PER_URL]:
        # Add the secret to the DB if not already exists
        if not get_secret(match_string=secret["match_string"]):
            add_secret(leak["pid"], secret["html_url"], secret["signature_name"], secret["match_string"])


def parse_secrets_results(repo_path, csv_path):
    secrets = []

    with open(csv_path) as csv_file:
        line_count = 0
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            # Skip the header row.
            if line_count == 0:
                line_count += 1
                continue

            commit_sha = row[2][1:]
            secrets.append({
                "signature_name": row[1],
                "commit_sha": commit_sha,
                "match_string": row[3],
                "html_url": repo_path[:-4] + "/commit/" + commit_sha
            })

            line_count += 1

    return secrets


# def trufflehog_parse_output(url, output):
#     secrets = []
#
#     results = []
#     # Limit the number of secrets to handle.
#     for foundIssue in output["foundIssues"]:
#         with open(foundIssue, "r") as issue_file:
#             results.append(json.loads(issue_file.read()))
#             # Structure
#             # dict_keys(['date', 'path', 'branch', 'commit'-msg, 'diff', 'stringsFound', 'printDiff', 'commitHash', 'reason'])
#
#     # Iterate over the results, and separate the strings found.
#     for res in results:
#         for string_found in res["stringsFound"]:
#             secrets.append({
#                 "signature_name": res["reason"],
#                 "commit_sha": res["commitHash"],
#                 "match_string": string_found,
#                 "html_url": url[:-4] + "/commit/" + res["commitHash"]
#             })
#
#     return secrets


# def scan_git(url):
#     output = truffleHog.find_strings(url, printJson=True, surpress_output=True, do_regex=False, do_entropy=True)
#     if output["foundIssues"]:
#         return trufflehog_parse_output(url, output)
#
#     truffleHog.clean_up(output)
#
#     return []


def scan(url, full_diff_dir):
    results_path = os.path.join(full_diff_dir, 'results.csv')

    subprocess.call([
        '/usr/local/bin/shhgit',
        '-config-path',
        '/app/secrets/',
        '-silent',
        '-csv-path',
        results_path,
        '-local',
        full_diff_dir,
    ])

    base_secrets = parse_secrets_results(url, results_path)
    # git_secrets = scan_git(url)
    # total_secrets = base_secrets + git_secrets
    # store_secrets(url, total_secrets)
    store_secrets(url, base_secrets)
