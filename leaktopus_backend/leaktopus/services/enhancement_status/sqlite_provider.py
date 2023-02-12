from leaktopus.services.enhancement_status.provider_interface import (
    EnhancementStatusProviderInterface,
)
from leaktopus.services.enhancement_status.enhancement_status import EnhancementStatus
from leaktopus.services.enhancement_status.enhancement_status_service import EnhancementStatusException
from leaktopus.utils.common_imports import logger
from leaktopus.utils.funcs import get_last_id


class EnhancementStatusSqliteProvider(EnhancementStatusProviderInterface):
    def __init__(self, options):
        self.db = options["db"]

    def get_enhancement_status(self, **kwargs) -> list[EnhancementStatus]:
        sql_cond = []
        sql_vars = ()
        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        c = self.db.cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            res = c.execute("SELECT * FROM enhancement_status WHERE " + where_str, sql_vars)
        else:
            res = c.execute("SELECT * FROM enhancement_status")

        contributors_res = res.fetchall()

        return self.to_entity(contributors_res)

    def add_enhancement_status(self, leak_url, search_query, module_key, last_modified, **kwargs) -> EnhancementStatus:
        try:
            c = self.db.cursor()
            c.execute('''
                    INSERT OR IGNORE INTO enhancement_status(leak_url, search_query, module_key, last_modified)
                        VALUES(?,?,?,?)
                    ''', (leak_url, search_query, module_key, last_modified,))
            self.db.commit()
            return get_last_id(self.db, "enhancement_status", c.lastrowid, "id")
        except self.db.Error as e:
            logger.error("Could not add enhancement status to DB: {}", e)
            self.db.rollback()
            raise EnhancementStatusException("Could not add enhancement status")

    def update_enhancement_status(self, id, **kwargs) -> EnhancementStatus:
        c = self.db.cursor()
        # @todo Find a prettier way to do the dynamic update.
        for col in kwargs.keys():
            col_sql = col + "=?"
            value = kwargs[col]

            c.execute("UPDATE enhancement_module SET " + col_sql + " WHERE id=?", (value, id,))

        self.db.commit()
        return get_last_id(self.db, "enhancement_status", c.lastrowid, "id")

    def to_entity(self, rows):
        ret = []
        for row in rows:
            enhancement_status = EnhancementStatus(
                id=row[0],
                leak_url=row[1],
                search_query=row[2],
                module_key=row[3],
                last_modified=row[4],
            )
            ret.append(enhancement_status)
        return ret
