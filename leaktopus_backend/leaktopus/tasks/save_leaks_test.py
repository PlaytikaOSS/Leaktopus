import json
import re

import pytest

from leaktopus.common.scanner_async import datetime_to_timestamp, get_org_emails
from leaktopus.services.leak.leak_service import LeakService
from leaktopus.services.leak.memory_provider import LeakMemoryProvider

# TODO:
# - SaveLeaksTask should use a structured search result object, e.g [SearchResult, ...]
# - SaveLeaksTask should use a structured leak object, e.g [Leak, ...]
# - SaveLeaksTask shouldn't return a list of anything, as it should only be used to save leaks
# - Adjust def save_leaks(self, leaks) to use the new leak object
# Obvious tasks:
# - Add more tests
# - Extract clases to files/structure


class EmailExtractor:
    def __init__(self, organization_domains):
        self.organization_domains = organization_domains

    def extract_organization_emails(self, content):
        org_emails = set()
        emails = self.extract_emails_from_content(content)
        for email in emails:
            if email.split("@")[1] in self.organization_domains:
                org_emails.add(email)

        return list(org_emails)

    def extract_emails_from_content(self, content):
        return re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)

class SaveLeaksUseCase():
    def __init__(self, leak_service: LeakService, email_extractor: EmailExtractor):
        self.leak_service = leak_service
        self.email_extractor = email_extractor

    def run(self, search_results: [], search_query):
        grouped_results = []
        for search_result in search_results:
            org_emails = self.email_extractor.extract_organization_emails(json.dumps(search_result))
            leak_data = self.generate_leak_data(search_result, org_emails)
            is_url_exists = self.is_url_exists(grouped_results, search_result)
            self.append_or_update_group_result(grouped_results, is_url_exists, leak_data, search_query, search_result)

        self.leak_service.save_leaks(grouped_results)
        return grouped_results

    def append_or_update_group_result(self, grouped_results, is_url_exists, leak_data, search_query, search_result):
        if is_url_exists:
            existing_res_key = None
            for i,gr in enumerate(grouped_results):
                if gr['url'] == search_result['clone_url']:
                    existing_res_key = i

            grouped_results[existing_res_key]["leaks"].append(leak_data)
        else:
            grouped_results.append(self.generate_result(grouped_results, search_result, search_query, leak_data))

    def is_url_exists(self, grouped_results, search_result):
        is_url_exists = False
        for gr in grouped_results:
            if gr['url'] == search_result['clone_url']:
                is_url_exists = True
                break
        return is_url_exists

    def generate_leak_data(self, search_result, org_emails):
        return {
            "file_name": search_result['name'],
            "file_url": search_result['html_url'],
            "org_emails": org_emails
        }

    def generate_result(self, grouped_results, search_result, search_query, leak_data):
        return {
            "url": search_result["clone_url"],
            "last_modified": datetime_to_timestamp(search_result['repository']['last_modified']),
            "leaks": [leak_data],
            "search_query": search_query,
            "type": "github",
            "context": {
                "repo_name": search_result['repository']['name'],
                "owner": search_result['repository']['owner']['login'] if search_result['repository']['owner']['login'] else False,
                "repo_description": search_result['repository']['description'],
                "default_branch": search_result['repository']['default_branch'],
                "is_fork": search_result['repository']['fork'],
                "forks_count": search_result['repository']['forks_count'],
                "watchers_count": search_result['repository']['watchers_count'],
                "stargazers_count": search_result['repository']['stargazers_count'],
            }
        }

def test_should_save_leaks_successfully(search_results):
    organization_domains = [
        "example.com",
        "example.org",
    ]
    search_query = "test"
    use_case = SaveLeaksUseCase(
        leak_service=LeakService(LeakMemoryProvider(
            override_methods={
                "save_leaks": lambda leaks: None
            }
        )),
        email_extractor=EmailExtractor(organization_domains=organization_domains)
    )
    grouped_results = use_case.run(search_results=search_results, search_query=search_query)

    assert len(grouped_results) == 2

@pytest.fixture
def search_results():
     return [
        {
            "name": "test.txt",
            "html_url": "asdasdf",
            "clone_url": "aasd1",
            "repository": {
                "name": "test",
                "owner": {
                    "login": "test"
                },
                "description": "test",
                "default_branch": "master",
                "fork": False,
                "forks_count": 0,
                "watchers_count": 0,
                "stargazers_count": 0,
                "last_modified": "Sat, 19 Dec 2022 15:34:56 UTC"
            }
        },
         {
            "name": "test.txt",
            "html_url": "asdasdf",
            "clone_url": "aasd2",
            "repository": {
                "name": "test",
                "owner": {
                    "login": "test"
                },
                "description": "test",
                "default_branch": "master",
                "fork": False,
                "forks_count": 0,
                "watchers_count": 0,
                "stargazers_count": 0,
                "last_modified": "Sat, 19 Dec 2022 15:34:56 UTC"
            }
        },
         {
            "name": "test.txt",
            "html_url": "asdasdf",
            "clone_url": "aasd1",
            "repository": {
                "name": "test",
                "owner": {
                    "login": "test"
                },
                "description": "test",
                "default_branch": "master",
                "fork": False,
                "forks_count": 0,
                "watchers_count": 0,
                "stargazers_count": 0,
                "last_modified": "Sat, 19 Dec 2022 15:34:56 UTC"
            }
        }
    ]
