import psycopg2.extras

def create_photo(conn, image):
    sql = """
        INSERT INTO photos (id,imageUrl,pageUrl,summary,creator,date) VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur = conn.cursor()
    data = (image["id"], image["imageUrl"], image["pageUrl"], image["summary"], image["creator"], image["date"])
    print(type(data))
    cur.execute(sql, data)
    print("Table created successfully")
    conn.commit()

def get_random_photo(conn):
    sql = """ 
        SELECT COUNT(*) FROM photos
    """
    cur = conn.cursor()
    cur.execute(sql)
    result = str(cur.fetchone()[0])
    sql = """
        SELECT * FROM photos OFFSET floor(random()*%s) LIMIT 1;
    """
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(sql, (result,))
    return dict_cur.fetchone()

def get_all_photos(conn):
    sql = """
        SELECT * FROM photos
    """
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(sql)
    return dict_cur.fetchall()
    
def delete_photo(conn, _id):
    sql = """
            DELETE FROM photos WHERE id = %s;
        """
    cur = conn.cursor()
    cur.execute(sql, (_id,))
    conn.commit()
    print('deleted')