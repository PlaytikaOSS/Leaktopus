from leaktopus.services.enhancement_module.enhancement_module_provider import EnhancementModuleProviderInterface
from leaktopus.utils.common_imports import logger
import os
import subprocess
import csv
import json
from truffleHog import truffleHog
from leaktopus.common.db_handler import add_secret, get_secret

class EnhancementModuleSecretsProvider(EnhancementModuleProviderInterface):
    def __init__(self, override_methods={}, **kwargs):
        self.override_methods = override_methods
        self.max_secrets_per_url = kwargs.get("max_secrets_per_url", 30)

    def get_provider_name(self):
        return "secrets"

    def store_secrets(self, leak_service, url, secrets):
        # Filter by unique secrets.
        secrets_unique = list({v['match_string']: v for v in secrets}.values())

        # Get leak id from DB.
        leaks = leak_service.get_leaks(url=url)

        if not leaks:
            return False

        for secret in secrets_unique[0:self.max_secrets_per_url]:
            # Add the secret to the DB if not already exists
            if not get_secret(match_string=secret["match_string"]):
                add_secret(leaks[0].leak_id, secret["html_url"], secret["signature_name"], secret["match_string"])

    def parse_secrets_results(self, repo_path, csv_path):
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

    def trufflehog_parse_output(self, url, output):
        secrets = []

        results = []
        # Limit the number of secrets to handle.
        for foundIssue in output["foundIssues"]:
            with open(foundIssue, "r") as issue_file:
                results.append(json.loads(issue_file.read()))
                # Structure
                # dict_keys(['date', 'path', 'branch', 'commit'-msg, 'diff', 'stringsFound', 'printDiff', 'commitHash', 'reason'])

        # Iterate over the results, and separate the strings found.
        for res in results:
            for string_found in res["stringsFound"]:
                secrets.append({
                    "signature_name": res["reason"],
                    "commit_sha": res["commitHash"],
                    "match_string": string_found,
                    "html_url": url[:-4] + "/commit/" + res["commitHash"]
                })

        return secrets

    def scan_git(self, url):
        output = truffleHog.find_strings(url, printJson=True, surpress_output=True, do_regex=False, do_entropy=True)
        if output["foundIssues"]:
            return self.trufflehog_parse_output(url, output)

        truffleHog.clean_up(output)

        return []

    def execute(self, potential_leak_source_request, leak_service, url, full_diff_dir):
        logger.info("Enhancement module secrets is enhancing PLS {} stored in {}", url, full_diff_dir)

        results_path = os.path.join(full_diff_dir, 'results.csv')

        logger.debug("Scanning {} with Shhgit", url)
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
        logger.debug("Shhgit scan for {} has been completed", url)

        base_secrets = self.parse_secrets_results(url, results_path)
        logger.debug("Scanning {} with TruffleHog", url)
        git_secrets = self.scan_git(url)
        logger.debug("TruffleHog scan for {} has been completed", url)
        total_secrets = base_secrets + git_secrets
        self.store_secrets(leak_service, url, total_secrets)
