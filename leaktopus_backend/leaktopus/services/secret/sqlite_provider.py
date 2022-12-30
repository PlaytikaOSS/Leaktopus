from leaktopus.services.secret.provider_interface import (
    SecretProviderInterface,
)
from leaktopus.services.secret.secret import Secret
from leaktopus.services.secret.secret_service import SecretException
from leaktopus.utils.common_imports import logger
from leaktopus.utils.funcs import get_last_id


class SecretSqliteProvider(SecretProviderInterface):
    def __init__(self, options):
        self.db = options["db"]

    def get_secrets(self, **kwargs) -> list[Secret]:
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
            res = c.execute("SELECT * FROM secret WHERE " + where_str + " ORDER BY created_at DESC", sql_vars)
        else:
            res = c.execute("SELECT * FROM secret ORDER BY created_at DESC")

        secrets_res = res.fetchall()

        return self.to_entity(secrets_res)

    def add_secret(self, leak_id, url, signature_name, match_string, **kwargs):
        # Insert or ignore if already exists.
        try:
            c = self.db.cursor()
            c.execute("""
                INSERT OR IGNORE INTO secret(leak_id, url, signature_name, match_string)
                    VALUES(?,?,?,?)
                """, (leak_id, url, signature_name, match_string,))
            self.db.commit()

            return get_last_id(self.db, "secret", c.lastrowid, "pid")
        except self.db.IntegrityError as err:
            self.db.rollback()
            raise SecretException("Secret already exists")
        except self.db.Error as e:
            logger.error("Could not add secret to DB: {}", e)
            self.db.rollback()
            raise SecretException("Could not add secret")

    def to_entity(self, rows):
        ret = []
        for row in rows:
            secret = Secret(
                row["pid"],
                row["leak_id"],
                row["url"],
                row["signature_name"],
                row["match_string"],
                row["created_at"]
            )
            ret.append(secret)
        return ret
