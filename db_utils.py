import psycopg2.extras

def create_photo(conn, image):
    try:
        print(image["id"])
        sql = """
            INSERT INTO photos (id,imageUrl,pageUrl,summary,creator,date,subject) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """
        cur = conn.cursor()
        data = (image["id"], image["imageUrl"], image["pageUrl"], image["summary"], image["creator"], image["date"], image["subject"])
        cur.execute(sql, data)
        conn.commit()
    except Exception as e:
        print(e)

def get_photo(conn, id):
    sql = """
        SELECT *
        FROM photos
        WHERE ID = %s
    """
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(sql, (id,))
    return dict_cur.fetchone()

def add_shared_photo(conn, id):
    sql = """
        INSERT INTO shared_photos (id) VALUES (%s)
    """
    cur = conn.cursor()
    cur.execute(sql, (id, ))
    conn.commit()

def get_random_photo(conn, list):
    sql1 = """
        SELECT COUNT(*) FROM photos
    """
    cur = conn.cursor()
    cur.execute(sql1)
    num = cur.fetchone()
    result = int(num[0]) - len(list)
    placeholder= '%s' 
    placeholders = ', '.join(placeholder for unused in list)
    sql = "SELECT * FROM photos WHERE id NOT IN (%s) OFFSET floor(random()*%s) LIMIT 1" % (placeholders, result)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(sql, list)
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

def delete_photo_by_subject(conn, string):
    search_term = "%" + string + "%"
    sql = """
            DELETE FROM photos WHERE subject LIKE %s;
        """
    cur = conn.cursor()
    cur.execute(sql, (search_term,))
    conn.commit()

def delete_photo_not_include_subject(conn, string):
    search_term = "%" + string + "%"
    sql = """
            DELETE FROM photos WHERE subject NOT LIKE %s;
        """
    cur = conn.cursor()
    cur.execute(sql, (search_term,))
    conn.commit()

def delete_photo_by_summary(conn, string):
    search_term = "%" + string + "%"
    sql = """
            DELETE FROM photos WHERE summary LIKE %s;
        """
    cur = conn.cursor()
    cur.execute(sql, (search_term,))
    conn.commit()

def delete_all_shared_photos(conn):
    sql = """
            DELETE FROM shared_photos;
        """
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

def get_unshared_photos(conn):
    sql = """ 
        SELECT COUNT(*) 
        FROM photos 
        WHERE id NOT IN (SELECT id FROM shared_photos)
    """
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()