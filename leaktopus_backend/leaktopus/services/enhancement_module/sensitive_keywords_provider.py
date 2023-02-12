import os
import hashlib
from leaktopus.services.enhancement_module.enhancement_module_provider import EnhancementModuleProviderInterface
from leaktopus.services.enhancement_module.enhancement_module_service import EnhancementModuleException
from leaktopus.utils.common_imports import logger
from leaktopus.common.sensitive_keywords import add_sensitive_keyword, get_sensitive_keywords

class EnhancementModuleSensitiveKeywordsProvider(EnhancementModuleProviderInterface):
    def __init__(self, override_methods={}, **kwargs):
        self.override_methods = override_methods

    def get_provider_name(self):
        return "sensitive_keywords"

    def get_sensitive_keyword_checksum(self, sensitive_keywords):
        sensitive_keywords_str = sensitive_keywords['keyword'] + \
                                 sensitive_keywords['url']
        return hashlib.md5(sensitive_keywords_str.encode('utf-8')).hexdigest()

    def get_existing_sensitive_keywords_checksums(self, leak):
        existing_sensitive_keywords_checksums = []
        existing_sensitive_keywords = get_sensitive_keywords(leak_id=leak.leak_id)

        for keyword in existing_sensitive_keywords:
            existing_sensitive_keywords_checksums.append(self.get_sensitive_keyword_checksum(keyword))

        return existing_sensitive_keywords_checksums

    def get_github_commit_url(self, repo_url, commit_hash):
        base_url = repo_url.removesuffix('.git')
        return f'{base_url}/commit/{commit_hash}'

    def parse_sensitive_keywords_results(self, leak_service, url, matches):
        # Get leak id from DB.
        leaks = leak_service.get_leaks(url=url)

        # Exit in case that the leak wasn't found.
        if not leaks:
            raise EnhancementModuleException(f"Cannot find leak for {url}")

        # Calc existing sensitive keywords checksums to decide whether new should be inserted to DB.
        existing_sensitive_keywords_checksums = self.get_existing_sensitive_keywords_checksums(leaks[0])

        for match in matches:
            sensitive_keyword = {
                'keyword': match["keyword"],
                'url': self.get_github_commit_url(url, match["sha"])
            }
            sensitive_keyword_checksum = self.get_sensitive_keyword_checksum(sensitive_keyword)

            # Add the contributor to the DB if not already exists.
            if sensitive_keyword_checksum not in existing_sensitive_keywords_checksums:
                add_sensitive_keyword(
                    leaks[0].leak_id,
                    sensitive_keyword['keyword'],
                    sensitive_keyword['url']
                )

    def search_str_in_direcotry(self, strings, dir):
        results = []

        for file in os.listdir(dir):
            path = dir + "/" + file
            if os.path.isdir(path):
                self.search_str_in_direcotry(path, strings)
            else:
                matches = {x for x in strings if x in open(path).read()}
                for m in matches:
                    results.append({"sha": file, "keyword": m})

        return results

    def execute(self, potential_leak_source_request, leak_service, url, full_diff_dir):
        logger.info("Enhancement module sensitive keywords is enhancing PLS {} stored in {}", url, full_diff_dir)

        # Remove empty strings from our list.
        sensitive_keywords_clean = list(filter(None, potential_leak_source_request.sensitive_keywords))

        if not sensitive_keywords_clean:
            return False

        try:
            matches = self.search_str_in_direcotry(potential_leak_source_request.sensitive_keywords, full_diff_dir)
            self.parse_sensitive_keywords_results(leak_service, url, matches)
        except Exception as e:
            logger.error("Error while extracting sensitive keywords for {} - {}", url, e)
            return False

        logger.debug("Done extracting sensitive keywords from {}", url)
