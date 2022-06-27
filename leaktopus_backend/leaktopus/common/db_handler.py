import sqlite3
from flask import Flask, g, abort
import os
import re
import leaktopus.common.scans as scans
import leaktopus.common.contributors as contributors
import leaktopus.common.sensitive_keywords as sensitive_keywords
import leaktopus.common.updates as updates
import leaktopus.common.db_updates as db_updates

app = Flask(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def regexp(expr, item):
    return re.search(rf"{expr}", item) is not None


def init_config_github_ignore(db):
    cursor = db.cursor()
    # Install the default ignore list.
    cursor.execute('''INSERT INTO config_github_ignore(pattern) VALUES
             ("^https://github.com/citp/privacy-policy-historical"),
             ("^https://github.com/haonanc/GDPR-data-collection"),
             ("^https://github.com/[\w\-]+/dmca")
             ''')
    db.commit()


def db_install(db):
    """
    First time DB initialization.
    :param db:
    :return:
    """
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE leak(
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                search_query TEXT,
                leak_type TEXT,
                context TEXT,
                leaks TEXT,
                acknowledged TINYINT,
                last_modified INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

    cursor.execute('''
            CREATE TABLE secret(
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                leak_id INTEGER,
                url TEXT,
                signature_name TEXT,
                match_string TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

    cursor.execute('''
            CREATE TABLE domain(
                pid INTEGER PRIMARY KEY AUTOINCREMENT,
                leak_id INTEGER,
                url TEXT,
                domain TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

    cursor.execute('''
            CREATE TABLE config_github_ignore(pid INTEGER PRIMARY KEY AUTOINCREMENT, pattern TEXT UNIQUE)
            ''')

    cursor.execute('''
                CREATE TABLE alert(
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sent_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    leak_id INTEGER,
                    type TEXT
                )''')
    db.commit()

    # Make some further installation steps.
    init_config_github_ignore(db)
    updates.db_install_updates(db)
    scans.db_install_scans(db)
    contributors.db_install_contributors(db)
    sensitive_keywords.db_install_sensitive_keywords(db)

    # Update the DB with the latest updates version.
    db_updates.apply_db_updates(True)


def get_db():
    db_path = os.environ.get('DB_PATH', "/tmp/leaktopus.sqlite")

    db = getattr(g, '_database', None)
    is_db_exists = os.path.isfile(db_path)

    if db is None:
        db = g._database = sqlite3.connect(db_path)
        db.create_function("REGEXP", 2, regexp)
        db.row_factory = dict_factory

        if not is_db_exists:
            db_install(db)

    return db


def get_alert(**kwargs):
    try:
        sql_cond = []
        sql_vars = ()
        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        cur = get_db().cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            res = cur.execute("SELECT * FROM alert WHERE " + where_str, sql_vars)
        else:
            res = cur.execute('''SELECT * FROM alert''')
        return res.fetchall()

    except Exception as e:
        abort(500)


def add_alert(leak_id, type):
    try:
        # Insert or ignore if already exists
        db = get_db()

        cursor = db.cursor()
        cursor.execute('''
                INSERT OR IGNORE INTO alert(leak_id, "type")
                    VALUES(?,?)
                ''', (leak_id, type,))
        db.commit()
        return cursor.lastrowid

    except Exception as e:
        abort(500)


def get_leak(**kwargs):
    try:
        sql_cond = []
        sql_vars = ()
        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        cur = get_db().cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            # @todo Replace this dirty workaround in a way that supports operators.
            where_str = where_str.replace("created_at=?", "created_at>?")
            res = cur.execute("SELECT * FROM leak WHERE " + where_str + " ORDER BY created_at DESC", sql_vars)
        else:
            res = cur.execute("SELECT * FROM leak ORDER BY created_at DESC")

        leaks_res = res.fetchall()
        # @todo Replace the secrets fetching with one query with join and grouping.
        for i in range(len(leaks_res)):
            secrets_res = cur.execute("SELECT * FROM secret WHERE leak_id=? ORDER BY created_at DESC", (leaks_res[i]["pid"],))
            leaks_res[i]["secrets"] = secrets_res.fetchall()

            domains_res = cur.execute("SELECT * FROM domain WHERE leak_id=? ORDER BY created_at DESC", (leaks_res[i]["pid"],))
            leaks_res[i]["domains"] = domains_res.fetchall()

            domains_res = cur.execute("SELECT id, name, author_email, committer_email, is_organization_domain FROM contributors WHERE leak_id=? ORDER BY created_at DESC", (leaks_res[i]["pid"],))
            leaks_res[i]["contributors"] = domains_res.fetchall()

            domains_res = cur.execute("SELECT id, keyword, url FROM sensitive_keywords WHERE leak_id=? ORDER BY created_at DESC", (leaks_res[i]["pid"],))
            leaks_res[i]["sensitive_keywords"] = domains_res.fetchall()

        return leaks_res

    except Exception as e:
        print(e)
        abort(500)


def get_secret(**kwargs):
    try:
        sql_cond = []
        sql_vars = ()
        for col in kwargs.keys():
            sql_vars = (*sql_vars, kwargs[col])
            sql_cond.append(col)

        cur = get_db().cursor()
        if sql_vars:
            where_str = ("=? AND ").join(sql_cond) + "=?"
            res = cur.execute("SELECT * FROM secret WHERE " + where_str + " ORDER BY created_at DESC", sql_vars)
        else:
            res = cur.execute('''SELECT * FROM secret ORDER BY created_at DESC''')
        return res.fetchall()

    except Exception as e:
        abort(500)


def add_secret(leak_id, url, signature_name, match_string):
    try:
        # Insert or ignore if already exists
        db = get_db()

        cursor = db.cursor()
        cursor.execute('''
                INSERT OR IGNORE INTO secret(leak_id, url, signature_name, match_string)
                    VALUES(?,?,?,?)
                ''', (leak_id, url, signature_name, match_string,))
        db.commit()
        return cursor.lastrowid

    except Exception as e:
        abort(500)


def get_domain(**kwargs):
    sql_cond = []
    sql_vars = ()
    for col in kwargs.keys():
        sql_vars = (*sql_vars, kwargs[col])
        sql_cond.append(col)

    cur = get_db().cursor()
    if sql_vars:
        where_str = ("=? AND ").join(sql_cond) + "=?"
        res = cur.execute("SELECT * FROM domain WHERE " + where_str + " ORDER BY created_at DESC", sql_vars)
    else:
        res = cur.execute('''SELECT * FROM domain ORDER BY created_at DESC''')
    return res.fetchall()


def add_domain(leak_id, url, domain):
    # Insert or ignore if already exists
    db = get_db()

    cursor = db.cursor()
    cursor.execute('''
            INSERT OR IGNORE INTO domain(leak_id, url, domain)
                VALUES(?,?,?)
            ''', (leak_id, url, domain,))
    db.commit()
    return cursor.lastrowid


# @todo Consider to use **kwargs instead.
def add_leak(url, search_query, leak_type, context, leaks, acknowledged, last_modified):
    try:
        # Insert or ignore if already exists
        db = get_db()

        cursor = db.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO leak(url, search_query, leak_type, context, leaks, acknowledged, last_modified)
                VALUES(?,?,?,?,?,?,?)
            ''', (url,search_query,leak_type,context,leaks,acknowledged,last_modified,))
        db.commit()
        return cursor.lastrowid

    except Exception as e:
        abort(500)


def update_leak(leak_id, **kwargs):
    # Insert or ignore if already exists
    db = get_db()

    # @todo Find a prettier way to do the dynamic update.
    for col in kwargs.keys():
        col_sql = col + "=?"
        db.cursor().execute("UPDATE leak SET " + col_sql + " WHERE pid=?", (kwargs[col],leak_id,))
    db.commit()


def delete_leak_by_url(url):
    db = get_db()
    cur = db.cursor()

    cur.execute('''DELETE FROM leak WHERE url REGEXP ?''', (url,))
    cur.execute('''DELETE FROM secret WHERE url REGEXP ?''', (url,))
    cur.execute('''DELETE FROM domain WHERE url REGEXP ?''', (url,))

    db.commit()


def get_config_github_ignored():
    cur = get_db().cursor()
    res = cur.execute('''SELECT pid as id, pattern FROM config_github_ignore''')
    return res.fetchall()


def add_config_github_ignored(pattern):
    try:
        # Insert or ignore if already exists
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''INSERT OR IGNORE INTO config_github_ignore(pattern) VALUES(?)''', (pattern,))
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        abort(500)


def delete_config_github_ignored(pid):
    try:
        # Insert or ignore if already exists
        db = get_db()
        db.cursor().execute('''DELETE FROM config_github_ignore WHERE pid=?''', (pid,))
        db.commit()
    except Exception as e:
        abort(500)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
