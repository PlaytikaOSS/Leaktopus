from leaktopus.services.leak.provider_interface import (
    LeakProviderInterface,
)
from leaktopus.services.leak.leak import Leak
from leaktopus.services.leak.leak_service import LeakException
from leaktopus.utils.common_imports import logger
from leaktopus.utils.funcs import get_last_id


class LeakSqliteProvider(LeakProviderInterface):
    def __init__(self, options):
        self.db = options["db"]

    def get_leaks(self, **kwargs) -> list[Leak]:
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
            res = c.execute("SELECT * FROM leak WHERE " + where_str + " ORDER BY created_at DESC", sql_vars)
        else:
            res = c.execute("SELECT * FROM leak ORDER BY created_at DESC")

        leaks_res = res.fetchall()

        # @todo Replace the secrets fetching with one query with join and grouping.
        for i in range(len(leaks_res)):
            secrets_res = c.execute("SELECT * FROM secret WHERE leak_id=? ORDER BY created_at DESC",
                                      (leaks_res[i]["pid"],))
            leaks_res[i]["secrets"] = secrets_res.fetchall()

            domains_res = c.execute("SELECT * FROM domain WHERE leak_id=? ORDER BY created_at DESC",
                                      (leaks_res[i]["pid"],))
            leaks_res[i]["domains"] = domains_res.fetchall()

            domains_res = c.execute(
                "SELECT id, name, author_email, committer_email, is_organization_domain FROM contributors WHERE leak_id=? ORDER BY created_at DESC",
                (leaks_res[i]["pid"],))
            leaks_res[i]["contributors"] = domains_res.fetchall()

            domains_res = c.execute(
                "SELECT id, keyword, url FROM sensitive_keywords WHERE leak_id=? ORDER BY created_at DESC",
                (leaks_res[i]["pid"],))
            leaks_res[i]["sensitive_keywords"] = domains_res.fetchall()

        return self.to_entity(leaks_res)

    def add_leak(self, url, search_query, leak_type, context, leaks, acknowledged, last_modified, **kwargs):
        # Insert or ignore if already exists.
        try:
            c = self.db.cursor()
            c.execute('''
                INSERT OR IGNORE INTO leak(url, search_query, leak_type, context, leaks, acknowledged, last_modified)
                    VALUES(?,?,?,?,?,?,?)
                ''', (url, search_query, leak_type, context, leaks, acknowledged, last_modified,))
            self.db.commit()

            return get_last_id(self.db, "leak", c.lastrowid, "pid")
        except self.db.IntegrityError as err:
            self.db.rollback()
            raise LeakException("Leak already exists")
        except self.db.Error as e:
            logger.error("Could not add leak to DB: {}", e)
            self.db.rollback()
            raise LeakException("Could not add leak")

    def update_leak(self, leak_id, **kwargs):
        # @todo Find a prettier way to do the dynamic update.
        for col in kwargs.keys():
            col_sql = col + "=?"
            self.db.cursor().execute("UPDATE leak SET " + col_sql + " WHERE pid=?", (kwargs[col], leak_id,))
        self.db.commit()

    def delete_leak_by_url(self, url, **kwargs):
        c = self.db.cursor()

        c.execute('''DELETE FROM leak WHERE url REGEXP ?''', (url,))
        # @todo Get the leak id and delete by it.
        c.execute('''DELETE FROM secret WHERE url REGEXP ?''', (url,))
        c.execute('''DELETE FROM domain WHERE url REGEXP ?''', (url,))
        # c.execute('''DELETE FROM contributors WHERE url REGEXP ?''', (url,))
        # c.execute('''DELETE FROM sensitive_keywords WHERE url REGEXP ?''', (url,))

        self.db.commit()

    def to_entity(self, rows):
        ret = []
        for row in rows:
            leak = Leak(
                row["pid"],
                row["url"],
                row["search_query"],
                row["leak_type"],
                row["context"],
                row["leaks"],
                row["acknowledged"],
                row["last_modified"],
                row["created_at"]
            )
            ret.append(leak)
        return ret
