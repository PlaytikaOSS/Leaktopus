import leaktopus.common.db_handler as dbh


def db_install_sensitive_keywords(db):
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE sensitive_keywords(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                leak_id INTEGER,
                keyword TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    db.commit()


def get_sensitive_keywords(**kwargs):
    sql_cond = []
    sql_vars = ()
    for col in kwargs.keys():
        sql_vars = (*sql_vars, kwargs[col])
        sql_cond.append(col)

    cur = dbh.get_db().cursor()
    if sql_vars:
        where_str = ("=? AND ").join(sql_cond) + "=?"
        res = cur.execute("SELECT * FROM sensitive_keywords WHERE " + where_str + " ORDER BY created_at DESC", sql_vars)
    else:
        res = cur.execute('''SELECT * FROM sensitive_keywords ORDER BY created_at DESC''')
    return res.fetchall()


def add_sensitive_keyword(leak_id, keyword, url):
    # Insert or ignore if already exists
    db = dbh.get_db()

    cursor = db.cursor()
    cursor.execute('''
            INSERT OR IGNORE INTO sensitive_keywords(leak_id, keyword, url)
                VALUES(?,?,?)
            ''', (leak_id, keyword, url,))
    db.commit()
    return cursor.lastrowid
