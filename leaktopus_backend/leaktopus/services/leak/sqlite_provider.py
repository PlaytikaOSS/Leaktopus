import json

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

    def fix_name_and_types_difference_between_db_and_entity(self, args):
        new_args = {}
        for key in args.keys():
            if key == "leak_id":
                new_args["pid"] = args.get(key)
            elif key == "type":
                new_args["leak_type"] = args.get(key)
            elif key == "iol":
                new_args["leaks"] = json.dumps(args.get(key))
            elif key == "context":
                new_args["context"] = json.dumps(args.get(key))
            else:
                new_args[key] = args.get(key)

        return new_args


    def get_leaks(self, **kwargs) -> list[Leak]:
        sql_cond = []
        sql_vars = ()
        filter_args = self.fix_name_and_types_difference_between_db_and_entity(kwargs)
        for col in filter_args.keys():
            sql_vars = (*sql_vars, filter_args[col])
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
        return self.to_entity(leaks_res)

    def add_leak(self, url, search_query, leak_type, context, iol, acknowledged, last_modified, **kwargs):
        # Insert or ignore if already exists.
        try:
            iol_str = json.dumps(iol)
            context_str = json.dumps(context)

            c = self.db.cursor()
            c.execute('''
                INSERT OR IGNORE INTO leak(url, search_query, leak_type, context, leaks, acknowledged, last_modified)
                    VALUES(?,?,?,?,?,?,?)
                ''', (url, search_query, leak_type, context_str, iol_str, acknowledged, last_modified,))
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
        prop_args = self.fix_name_and_types_difference_between_db_and_entity(kwargs)
        # @todo Find a prettier way to do the dynamic update.
        for col in prop_args.keys():
            col_sql = col + "=?"
            value = prop_args[col]

            self.db.cursor().execute("UPDATE leak SET " + col_sql + " WHERE pid=?", (value, leak_id,))
        self.db.commit()

    def update_iol(self, leak_id, iol):
        iol_str = json.dumps(iol)
        self.db.cursor().execute(
            '''UPDATE leak SET leaks = CASE WHEN NOT EXISTS (SELECT 1 FROM json_each(leaks) WHERE value = json(?)) THEN json_insert(leaks, "$[#]", json(?)) ELSE leaks END WHERE pid = ?''',
            (iol_str, iol_str, leak_id))
        self.db.commit()

    def delete_leak_by_url(self, url, **kwargs):
        c = self.db.cursor()
        c.execute('''DELETE FROM leak WHERE url REGEXP ?''', (url,))
        self.db.commit()

    def to_entity(self, rows):
        ret = []
        for row in rows:
            leak = Leak(
                row["pid"],
                row["url"],
                row["search_query"],
                row["leak_type"],
                json.loads(row["context"]),
                json.loads(row["leaks"]),
                row["acknowledged"],
                row["last_modified"],
                row["created_at"]
            )
            ret.append(leak)
        return ret
