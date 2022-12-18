import leaktopus.common.db_handler as dbh


def db_install_contributors(db):
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE if not exists contributors(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leak_id INTEGER,
                name TEXT,
                author_email TEXT,
                committer_email TEXT,
                is_organization_domain INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    db.commit()


def get_contributors(**kwargs):
    sql_cond = []
    sql_vars = ()
    for col in kwargs.keys():
        sql_vars = (*sql_vars, kwargs[col])
        sql_cond.append(col)

    cur = dbh.get_db().cursor()
    if sql_vars:
        where_str = ("=? AND ").join(sql_cond) + "=?"
        res = cur.execute("SELECT * FROM contributors WHERE " + where_str + " ORDER BY created_at DESC", sql_vars)
    else:
        res = cur.execute('''SELECT * FROM contributors ORDER BY created_at DESC''')
    return res.fetchall()


def add_contributor(leak_id, name, author_email, committer_email, is_organization_domain):
    # Insert or ignore if already exists
    db = dbh.get_db()

    cursor = db.cursor()
    cursor.execute('''
            INSERT OR IGNORE INTO contributors(leak_id, name, author_email, committer_email, is_organization_domain)
                VALUES(?,?,?,?,?)
            ''', (leak_id, name, author_email, committer_email, is_organization_domain,))
    db.commit()
    return cursor.lastrowid
