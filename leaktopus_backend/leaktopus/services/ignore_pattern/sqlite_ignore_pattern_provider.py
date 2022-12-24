from abc import abstractmethod
from typing import Protocol

from leaktopus.services.ignore_pattern.ignore_pattern_provider_interface import (
    IgnorePatternProviderInterface,
)


class SqliteIgnorePatternProvider(IgnorePatternProviderInterface):
    def __init__(self, db, provider: IgnorePatternProviderInterface = None):
        self.db = db

    def get_ignore_patterns(self):
        cur = self.db.cursor()
        res = cur.execute("""SELECT pid as id, pattern FROM config_github_ignore""")
        return res.fetchall()
