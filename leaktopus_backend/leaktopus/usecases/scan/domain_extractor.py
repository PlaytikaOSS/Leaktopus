import re
from typing import List


class DomainExtractor:
    def __init__(self, ltds: List[str]):
        self.ltds = ltds

    def extract(self, content):
        # Find all domains (common extensions only) in the content.
        # @todo Improve the extensions list.
        ltds_string = "|".join(self.ltds)
        ltds_regex = "[\w\.-]+\.(?:{})".format(ltds_string)
        domains = re.findall(r"{}".format(ltds_regex), content, re.MULTILINE)
        return domains
