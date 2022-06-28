from subprocess import run, CalledProcessError
import hashlib
from leaktopus.common.sensitive_keywords import add_sensitive_keyword, get_sensitive_keywords
from leaktopus.common.leak_handler import get_leak_by_url


def is_contributor_org_domain(author_email, committer_email, organization_domains):
    contributors_domains = set()
    contributors_domains.add(author_email.split('@')[1])
    contributors_domains.add(committer_email.split('@')[1])

    for domain in contributors_domains:
        if domain in organization_domains:
            return True

    return False


def add_sensitive_keyword_to_db(leak, sensitive_keyword):
    return add_sensitive_keyword(
                leak["pid"],
                sensitive_keyword['keyword'],
                sensitive_keyword['url']
            )


def get_sensitive_keyword_checksum(sensitive_keywords):
    sensitive_keywords_str = sensitive_keywords['keyword'] + \
                      sensitive_keywords['url']
    return hashlib.md5(sensitive_keywords_str.encode('utf-8')).hexdigest()


def get_existing_sensitive_keywords_checksums(leak):
    existing_sensitive_keywords_checksums = []
    existing_sensitive_keywords = get_sensitive_keywords(leak_id=leak['pid'])

    for keyword in existing_sensitive_keywords:
        existing_sensitive_keywords_checksums.append(get_sensitive_keyword_checksum(keyword))

    return existing_sensitive_keywords_checksums


def get_github_commit_url(repo_url, commit_hash):
    base_url = repo_url.rstrip('.git')
    return f'{base_url}/commit/{commit_hash}'


def parse_sensitive_keywords_results(url, output):
    # Get leak id from DB.
    leak = get_leak_by_url(url)

    # Exit in case that the leak wasn't found.
    # @todo Replace with exception.
    if not leak:
        return False

    # Calc existing sensitive keywords checksums to decide whether new should be inserted to DB.
    existing_sensitive_keywords_checksums = get_existing_sensitive_keywords_checksums(leak)

    for row in output.splitlines():
        # @todo Support the case where there is ":" in the keyword.
        commit_hash, keyword = row.lstrip('./').split(': ')
        sensitive_keyword = {
            'keyword': keyword.strip('"'),
            'url': get_github_commit_url(url, commit_hash)
        }
        sensitive_keyword_checksum = get_sensitive_keyword_checksum(sensitive_keyword)

        # Add the contributor to the DB if not already exists.
        if sensitive_keyword_checksum not in existing_sensitive_keywords_checksums:
            add_sensitive_keyword_to_db(leak, sensitive_keyword)


def scan(url, full_diff_dir, sensitive_keywords):
    if not sensitive_keywords:
        return False

    # Add the -e prefix to all keywords for our grep.
    grep_keywords = [f'-e {keyword}' for keyword in sensitive_keywords]
    grep_cmd = ['grep', '-IiroF']
    grep_cmd.extend(grep_keywords)
    grep_cmd.append('.')

    try:
        output = run(grep_cmd,
                     check=True,
                     capture_output=True,
                     text=True,
                     cwd=full_diff_dir
                     ).stdout

        if output:
            parse_sensitive_keywords_results(url, output)
    except CalledProcessError:
        return False
