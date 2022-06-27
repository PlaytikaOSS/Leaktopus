import os
from subprocess import Popen, CalledProcessError, STDOUT, PIPE
import hashlib
from leaktopus.common.contributors import add_contributor, get_contributors
from leaktopus.common.leak_handler import get_leak_by_url


def is_contributor_org_domain(author_email, committer_email, organization_domains):
    contributors_domains = set()
    author_email_sep = author_email.split('@')
    committer_email_sep = committer_email.split('@')
    if len(author_email_sep) > 1:
        contributors_domains.add(author_email_sep[1])

    if len(committer_email_sep) > 1:
        contributors_domains.add(committer_email_sep[1])

    for domain in contributors_domains:
        if domain in organization_domains:
            return True

    return False


def add_contributor_to_db(leak, contributor):
    return add_contributor(
        leak["pid"],
        contributor['name'],
        contributor['author_email'],
        contributor['committer_email'],
        contributor['is_organization_domain']
    )


def get_contributor_checksum(contributor):
    contributor_str = contributor['name'] +\
                      contributor['author_email'] +\
                      contributor['committer_email']
    return hashlib.md5(contributor_str.encode('utf-8')).hexdigest()


def get_existing_contributors_checksums(leak):
    existing_contributors_checksums = []
    existing_contributors = get_contributors(leak_id=leak['pid'])

    for contributor in existing_contributors:
        existing_contributors_checksums.append(get_contributor_checksum(contributor))

    return existing_contributors_checksums


def parse_contributors_results(url, output, organization_domains):
    contributors = []

    for row in output.splitlines():
        row_parts = row.split("###")
        name = row_parts[0]
        committer_email = row_parts[1]
        author_email = row_parts[2]

        contributors.append({
            "name": name,
            "author_email": author_email,
            "committer_email": committer_email,
            "is_organization_domain": is_contributor_org_domain(author_email, committer_email, organization_domains)
        })

    uniq_contributors = [dict(s) for s in set(frozenset(d.items()) for d in contributors)]
    # Get leak id from DB.
    leak = get_leak_by_url(url)

    # Exit in case that the leak wasn't found.
    # @todo Replace with exception.
    if not leak:
        return False

    # Calc existing contributors checksums to decide whether new should be inserted to DB.
    existing_contributors_checksums = get_existing_contributors_checksums(leak)

    for contributor in uniq_contributors:
        contributor_checksum = get_contributor_checksum(contributor)

        # Add the contributor to the DB if not already exists.
        if contributor_checksum not in existing_contributors_checksums:
            add_contributor_to_db(leak, contributor)


def scan(url, full_diff_dir, organization_domains):
    try:
        # Using ### as a separator between the values.
        git_log_proc = Popen([
            'git',
            'log',
            '--pretty=format:%an###%ce###%aE'
        ], stdout=PIPE, cwd=full_diff_dir)
        # Sort and leave only unique lines for faster processing.
        proc2 = Popen(['sort', '-u'], stdin=git_log_proc.stdout, stdout=PIPE, stderr=PIPE)
        git_log_proc.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
        output, err = proc2.communicate()
        str_output = output.decode()

        if str_output:
            parse_contributors_results(url, str_output, organization_domains)
    except CalledProcessError:
        return False
