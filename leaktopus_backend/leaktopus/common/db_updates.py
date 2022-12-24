from sqlite3 import OperationalError
from loguru import logger
import leaktopus.common.db_handler as dbh
import leaktopus.common.updates as updates

DB_UPDATES_PREFIX = "db_update_"


def apply_db_updates(is_clean_install):
    """

    :param is_clean_install: Whether this is a clean initial installation (otherwise an update).
    :return:
    """
    # Get all done DB updates (to skip).
    done_updates = []

    # Get the db.
    db = dbh.get_db()

    try:
        done_updates = updates.get_updates(status=1)
    except OperationalError as e:
        if str(e).startswith("no such table:"):
            logger.info("Updates table not yet exists")
            pass

    # Get the update ids of done updates.
    done_update_ids = [update["update_id"] for update in done_updates]

    for key, value in globals().items():
        if callable(value) and key.startswith(DB_UPDATES_PREFIX):
            update_id = key[len(DB_UPDATES_PREFIX) :]
            if update_id not in done_update_ids:
                if not is_clean_install:
                    value(db)

                # Update as done in DB.
                updates.add_update(update_id)
                logger.info("DB Update #{} has been completed.", update_id)


# Add below update function with a unique number, those will be executed automatically on next update request.
def db_update_1001(db):
    updates.db_install_updates(db)


def db_update_1002(db):
    import leaktopus.common.scans as scans

    scans.db_install_scans(db)


def db_update_1003(db):
    import leaktopus.common.contributors as contributors

    contributors.db_install_contributors(db)


def db_update_1004(db):
    import leaktopus.common.sensitive_keywords as sensitive_keywords

    sensitive_keywords.db_install_sensitive_keywords(db)


# def db_update_1005(db):
#     logger.info("DB Update #1005 has been completed: {}.", db)
#     cursor = db.cursor()
#     cursor.execute(
#         """
#             CREATE TABLE IF NOT EXSITS scan_status (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 scan_id INTEGER,
#                 page_number INTEGER,
#                 status TEXT,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                 )
#         """
#     )
#     db.commit()
