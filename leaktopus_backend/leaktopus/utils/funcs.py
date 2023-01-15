from leaktopus.utils.common_imports import logger


# https://stackoverflow.com/a/15601039/554540
# SQLiteDatabase's insert() returns an integer primary key even if you defined
# another type of primary key in your table.
# Simply use the result from insert() to fetch your guid:
def get_last_id(db, table_name, last_row_id, id_key="id"):
    c = db.cursor()
    query = "SELECT {} FROM {} WHERE rowid=?".format(id_key, table_name)
    ret = c.execute(query, (last_row_id,)).fetchone()
    logger.debug("query: {} {}".format(query, ret))

    if id_key not in ret:
        raise Exception("id_key {} not in ret: {}".format(id_key, ret))
    return ret[id_key]


def create_index_if_not_exists(
    db, index_name: str, table_name: str, table_columns: list
):
    c = db.cursor()
    row = c.execute(
        """
            SELECT count(*) as c FROM sqlite_master WHERE type='index' and name='{index_name}'
        """.format(
            index_name=index_name
        )
    ).fetchone()
    if row["c"] == 0:
        c.execute(
            "CREATE INDEX {index_name} ON {table_name} ({table_columns})".format(
                index_name=index_name,
                table_name=table_name,
                table_columns=",".join(table_columns),
            )
        )
        db.commit()
