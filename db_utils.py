def create_photo(conn, image):
    sql = """
        INSERT INTO photos(id, imageUrl, pageUrl, summary, creator, date) VALUES(?, ?, ?, ?, ?, ?)"""
    cur = conn.cursor()
    cur.execute(sql, (image["id"], image["imageUrl"], image["pageUrl"], image["summary"], image["creator"], image["date"]))

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_random_photo(conn):
    sql = """
        SELECT * FROM photos
        WHERE _ROWID_ >= (abs(random()) % (SELECT max(_ROWID_) FROM photos))
        LIMIT 1
        """
    conn.row_factory = dict_factory
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()



