import leaktopus.common.db_handler as dbh


def db_install_updates(db):
    cursor = db.cursor()
    cursor.execute('''
                CREATE TABLE updates(
                    update_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status INTEGER
                )''')
    db.commit()


def get_updates(**kwargs):
    sql_cond = []
    sql_vars = ()

    for col in kwargs.keys():
        sql_vars = (*sql_vars, kwargs[col])
        sql_cond.append(col)

    cur = dbh.get_db().cursor()
    if sql_vars:
        where_str = ("=? AND ").join(sql_cond) + "=?"
        res = cur.execute("SELECT * FROM updates WHERE " + where_str, sql_vars)
    else:
        res = cur.execute('''SELECT * FROM updates''')

    return res.fetchall()


def add_update(update_id):
    # Insert or ignore if already exists
    db = dbh.get_db()

    cursor = db.cursor()
    cursor.execute('''
            INSERT OR IGNORE INTO updates(update_id, status)
                VALUES(?,?)
            ''', (update_id, 1,))
    db.commit()
    return cursor.lastrowid
