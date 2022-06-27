from leaktopus.models.scan_status import ScanStatus
import leaktopus.common.db_handler as dbh
from datetime import datetime


def db_install_scans(db):
    cursor = db.cursor()
    cursor.execute('''
                CREATE TABLE scans(
                    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_query TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status INTEGER
                )''')
    db.commit()


def get_scans(**kwargs):
    sql_cond = []
    sql_vars = ()

    for col in kwargs.keys():
        sql_vars = (*sql_vars, kwargs[col])
        sql_cond.append(col)

    cur = dbh.get_db().cursor()
    if sql_vars:
        where_str = ("=? AND ").join(sql_cond) + "=?"
        res = cur.execute("SELECT * FROM scans WHERE " + where_str, sql_vars)
    else:
        res = cur.execute('''SELECT * FROM scans''')

    scans = res.fetchall()

    # Get the name of the status from the ScanStatus Enum.
    for scan in scans:
        scan["status_human"] = ScanStatus(scan["status"]).name

    return scans


def add_scan(search_query):
    # Insert or ignore if already exists
    db = dbh.get_db()

    cursor = db.cursor()
    cursor.execute('''
            INSERT OR IGNORE INTO scans(search_query, status)
                VALUES(?,?)
            ''', (search_query, ScanStatus.SCAN_SEARCHING.value,))
    db.commit()
    return cursor.lastrowid


def update_scan(scan_id, **kwargs):
    # Insert or ignore if already exists
    db = dbh.get_db()

    for col in kwargs.keys():
        col_sql = col + "=?"
        db.cursor().execute("UPDATE scans SET " + col_sql + " WHERE scan_id=?", (kwargs[col],scan_id,))
    db.commit()


def update_scan_status(scan_id, new_status):
    # Do not update a completed scan.
    scan = get_scans(scan_id=scan_id)[0]
    if scan["status"] in (ScanStatus.SCAN_DONE.value, ScanStatus.SCAN_ABORTED.value, ScanStatus.SCAN_FAILED.value):
        return False

    if new_status.value in (ScanStatus.SCAN_DONE.value, ScanStatus.SCAN_ABORTED.value, ScanStatus.SCAN_FAILED.value):
        update_scan(scan_id, status=new_status.value, completed_at=datetime.now())
    else:
        update_scan(scan_id, status=new_status.value)

    return True


def get_running_scan_by_search_query(search_query):
    cur = dbh.get_db().cursor()
    res = cur.execute(
        "SELECT * FROM scans WHERE search_query =? AND status NOT IN (?, ?, ?)",
        (search_query, ScanStatus.SCAN_DONE.value, ScanStatus.SCAN_ABORTED.value, ScanStatus.SCAN_FAILED.value,)
    )
    return res.fetchall()


def is_scan_aborting(scan_id):
    scan = get_scans(scan_id=scan_id)
    return scan[0]["status"] == ScanStatus.SCAN_ABORTING.value
