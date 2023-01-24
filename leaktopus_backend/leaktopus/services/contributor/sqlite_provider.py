from leaktopus.services.contributor.provider_interface import (
    ContributorProviderInterface,
)
from leaktopus.services.contributor.contributor import Contributor
from leaktopus.services.contributor.contributor_service import ContributorException
from leaktopus.utils.common_imports import logger
from leaktopus.utils.funcs import get_last_id


class ContributorSqliteProvider(ContributorProviderInterface):
    def __init__(self, options):
        self.db = options["db"]

    def get_contributors(self, **kwargs) -> list[Contributor]:
        sql_cond = []
        sql_vars = ()
        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        c = self.db.cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            res = c.execute("SELECT * FROM contributors WHERE " + where_str, sql_vars)
        else:
            res = c.execute("SELECT * FROM contributors")

        contributors_res = res.fetchall()

        return self.to_entity(contributors_res)

    def add_contributor(self, leak_id, name, author_email, committer_email, is_organization_domain):
        try:
            c = self.db.cursor()
            c.execute('''
                    INSERT OR IGNORE INTO contributors(leak_id, name, author_email, committer_email, is_organization_domain)
                        VALUES(?,?,?,?,?)
                    ''', (leak_id, name, author_email, committer_email, is_organization_domain,))
            self.db.commit()
            return get_last_id(self.db, "contributor", c.lastrowid, "id")
        except self.db.IntegrityError as err:
            self.db.rollback()
            raise ContributorException("Contributor already exists")
        except self.db.Error as e:
            logger.error("Could not add contributor to DB: {}", e)
            self.db.rollback()
            raise ContributorException("Could not add contributor")

    def to_entity(self, rows):
        ret = []
        for row in rows:
            contributor = Contributor(
                row["id"],
                row["leak_id"],
                row["name"],
                row["author_email"],
                row["committer_email"],
                row["is_organization_domain"],
                row["created_at"],
            )
            ret.append(contributor)
        return ret
