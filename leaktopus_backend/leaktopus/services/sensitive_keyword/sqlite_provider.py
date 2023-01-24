from leaktopus.services.sensitive_keyword.provider_interface import (
    SensitiveKeywordProviderInterface,
)
from leaktopus.services.sensitive_keyword.sensitive_keyword import SensitiveKeyword
from leaktopus.services.sensitive_keyword.sensitive_keyword_service import SensitiveKeywordException
from leaktopus.utils.common_imports import logger
from leaktopus.utils.funcs import get_last_id


class SensitiveKeywordSqliteProvider(SensitiveKeywordProviderInterface):
    def __init__(self, options):
        self.db = options["db"]

    def get_sensitive_keywords(self, **kwargs) -> list[SensitiveKeyword]:
        sql_cond = []
        sql_vars = ()
        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        c = self.db.cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            # @todo Replace this dirty workaround in a way that supports operators.
            where_str = where_str.replace("created_at=?", "created_at>?")
            res = c.execute("SELECT * FROM sensitive_keywords WHERE " + where_str + " ORDER BY created_at DESC",
                            sql_vars)
        else:
            res = c.execute("SELECT * FROM sensitive_keywords ORDER BY created_at DESC")

        sensitive_keywords_res = res.fetchall()

        return self.to_entity(sensitive_keywords_res)

    def add_sensitive_keyword(self, leak_id, keyword, url, **kwargs):
        # Insert or ignore if already exists.
        try:
            c = self.db.cursor()
            c.execute(
                "INSERT OR IGNORE INTO sensitive_keywords(leak_id, keyword, url) VALUES(?,?,?)",
                (leak_id, keyword, url,),
            )
            self.db.commit()
            return get_last_id(self.db, "sensitive_keywords", c.lastrowid, "id")
        except self.db.IntegrityError as err:
            self.db.rollback()
            raise SensitiveKeywordException("Sensitive keyword already exists")
        except self.db.Error as e:
            logger.error("Could not add Sensitive keyword to DB: {}", e)
            self.db.rollback()
            raise SensitiveKeywordException("Could not add Sensitive keyword")

    def to_entity(self, rows):
        ret = []
        for row in rows:
            sensitive_keyword = SensitiveKeyword(
                row["id"], row["leak_id"], row["keyword"], row["url"], row["created_at"]
            )
            ret.append(sensitive_keyword)
        return ret
