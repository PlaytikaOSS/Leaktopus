import re
from typing import List


class DomainExtractor:
    def __init__(self, tlds: List[str]):
        self.tlds = tlds

    def extract(self, content):
        # Find all domains (common extensions only) in the content.
        # @todo Improve the extensions list.
        tlds_string = "|".join(self.tlds)
        tlds_regex = "[\w\.-]+\.(?:{})".format(tlds_string)
        domains = re.findall(r"{}".format(tlds_regex), content, re.MULTILINE)
        return domains
