from leaktopus.services.alert.provider_interface import (
    AlertProviderInterface,
)
from leaktopus.services.alert.alert import Alert
from leaktopus.services.alert.alert_service import AlertException
from leaktopus.utils.common_imports import logger
from leaktopus.utils.funcs import get_last_id


class AlertSqliteProvider(AlertProviderInterface):
    def __init__(self, options):
        self.db = options["db"]

    def get_alerts(self, **kwargs) -> list[Alert]:
        sql_cond = []
        sql_vars = ()

        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        c = self.db.cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            res = c.execute("SELECT * FROM alert WHERE " + where_str, sql_vars)
        else:
            res = c.execute("""SELECT * FROM alert""")

        rows = res.fetchall()
        return self.to_entity(rows)

    def add_alert(self, leak_id, type, **kwargs):
        # Insert or ignore if already exists.
        try:

            c = self.db.cursor()
            c.execute('''
                    INSERT OR IGNORE INTO alert(leak_id, "type")
                        VALUES(?,?)
                    ''', (leak_id, type,))
            self.db.commit()

            return get_last_id(self.db, "alert", c.lastrowid, "alert_id")
        except self.db.IntegrityError as err:
            self.db.rollback()
            raise AlertException("Alert already exists")
        except self.db.Error as e:
            logger.error("Could not add alert to DB: {}", e)
            self.db.rollback()
            raise AlertException("Could not add alert")

    def to_entity(self, rows):
        ret = []
        for row in rows:
            alert = Alert(
                row["alert_id"],
                row["sent_time"],
                row["leak_id"],
                row["type"],
            )
            ret.append(alert)
        return ret
