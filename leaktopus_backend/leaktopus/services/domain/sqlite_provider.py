from leaktopus.services.domain.domain import Domain
from leaktopus.services.domain.domain_service import DomainException
from leaktopus.services.domain.provider_interface import DomainProviderInterface

from leaktopus.utils.common_imports import logger
from leaktopus.utils.funcs import get_last_id


class DomainSqliteProvider(DomainProviderInterface):
    def __init__(self, options):
        self.db = options["db"]

    def get_domains(self, **kwargs) -> list[Domain]:
        sql_cond = []
        sql_vars = ()
        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        c = self.db.cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            res = c.execute("SELECT * FROM domain WHERE " + where_str, sql_vars)
        else:
            res = c.execute("SELECT * FROM domain")

        domains_res = res.fetchall()

        return self.to_entity(domains_res)

    def add_domain(self, leak_id, url, domain, **kwargs):
        try:
            c = self.db.cursor()
            c.execute(
                "INSERT OR IGNORE INTO domain(leak_id, url, domain) VALUES(?,?,?)",
                (leak_id, url, domain,),
            )
            self.db.commit()
            return get_last_id(self.db, "domain", c.lastrowid, "pid")
        except self.db.IntegrityError as err:
            self.db.rollback()
            raise DomainException("Domain already exists")
        except self.db.Error as e:
            logger.error("Could not add domain to DB: {}", e)
            self.db.rollback()
            raise DomainException("Could not add domain")

    def to_entity(self, rows):
        ret = []
        for row in rows:
            domain = Domain(
                row["pid"],
                row["leak_id"],
                row["url"],
                row["domain"],
                row["created_at"],
            )
            ret.append(domain)
        return ret
