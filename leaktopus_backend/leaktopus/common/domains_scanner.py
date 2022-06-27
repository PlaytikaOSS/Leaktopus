import os
from subprocess import check_output, CalledProcessError, STDOUT
import json
from leaktopus.common.db_handler import add_domain, get_domain
from leaktopus.common.leak_handler import get_leak_by_url


def parse_domains_results(url, output):
    domains = []

    for row in output.splitlines():
        row_parts = row.split(":")
        commit_sha = row_parts[0][2:]
        domains.append({
            "commit_sha": commit_sha,
            "domain": ':'.join(row_parts[1:]),
            "html_url": url[:-4] + "/commit/" + commit_sha
        })

    # Filter by unique domains.
    domains_unique = list({v['domain']: v for v in domains}.values())

    # Get leak id from DB.
    leak = get_leak_by_url(url)

    if not leak:
        return False

    for domain in domains_unique:
        # Add the secret to the DB if not already exists
        if not get_domain(domain=domain["domain"]):
            add_domain(leak["pid"], domain["html_url"], domain["domain"])


def scan(url, full_diff_dir, organization_domains):
    # @todo Consider to match also IP addresses.
    domains_matching = "([a-zA-Z])+?://([a-zA-Z0-9\.\-_])*(" + "|".join(organization_domains) + ")"
    try:
        output = check_output([
            'egrep',
            '-Iiro',
            domains_matching,
            "."
        ], stderr=STDOUT, cwd=full_diff_dir).decode()

        if output:
            parse_domains_results(url, output)
    except CalledProcessError:
        return False
