import psycopg2.extras

def create_photo(conn, image):
    try:
        print(image["id"])
        sql = """
            INSERT INTO photos (id,imageUrl,pageUrl,summary,format,date,subject) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """
        cur = conn.cursor()
        data = (image["id"], image["imageUrl"], image["pageUrl"], image["summary"], image["formatb"], image["date"], image["subject"])
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

def get_random_photo(conn, term=None):
    if term:
        sql = """
            SELECT * FROM photos_2024 
            WHERE (summary LIKE %s OR subject LIKE %s)
            ORDER BY random()
            LIMIT 1
        """
        term_with_wildcards = f"%{term}%"

        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute(sql, (term_with_wildcards, term_with_wildcards))
        return dict_cur.fetchone()
    else:
        sql = """
            SELECT * FROM photos_2024
            WHERE collection LIKE '%Western%' AND subject LIKE '%Colorado%' AND subject NOT LIKE '%Locomotive%'
            ORDER BY random()
            LIMIT 1
        """
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute(sql)
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