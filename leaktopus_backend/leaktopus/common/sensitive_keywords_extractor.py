from subprocess import run, CalledProcessError
import hashlib
import os
from loguru import logger
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
    base_url = repo_url.removesuffix('.git')
    return f'{base_url}/commit/{commit_hash}'


def parse_sensitive_keywords_results(url, matches):
    # Get leak id from DB.
    leak = get_leak_by_url(url)

    # Exit in case that the leak wasn't found.
    if not leak:
        raise Exception(f"Cannot find leak for {url}")

    # Calc existing sensitive keywords checksums to decide whether new should be inserted to DB.
    existing_sensitive_keywords_checksums = get_existing_sensitive_keywords_checksums(leak)

    for match in matches:
        sensitive_keyword = {
            'keyword': match["keyword"],
            'url': get_github_commit_url(url, match["sha"])
        }
        sensitive_keyword_checksum = get_sensitive_keyword_checksum(sensitive_keyword)

        # Add the contributor to the DB if not already exists.
        if sensitive_keyword_checksum not in existing_sensitive_keywords_checksums:
            add_sensitive_keyword_to_db(leak, sensitive_keyword)


def search_str_in_direcotry(strings, dir):
    import os
    results = []

    for file in os.listdir(dir):
        path = dir + "/" + file
        if os.path.isdir(path):
            search_str_in_direcotry(path, strings)
        else:
            matches = {x for x in strings if x in open(path).read()}
            for m in matches:
                results.append({"sha": file, "keyword": m})

    return results


def scan(url, full_diff_dir, sensitive_keywords):
    logger.debug("Extracting sensitive keywords from {}", url)
    # Remove empty strings from our list.
    sensitive_keywords_clean = list(filter(None, sensitive_keywords))

    if not sensitive_keywords_clean:
        return False

    try:
        matches = search_str_in_direcotry(sensitive_keywords, full_diff_dir)
        parse_sensitive_keywords_results(url, matches)
    except Exception as e:
        logger.error("Error while extracting sensitive keywords for {} - {}", url, e)
        return False

    logger.debug("Done extracting sensitive keywords from {}", url)
