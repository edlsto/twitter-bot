import psycopg2.extras
import logging

logging.basicConfig(level=logging.INFO)

def get_random_photo(conn, term=None):
    try:
        if term:
            sql = """
                SELECT * FROM photos_2024 
                WHERE (summary LIKE %s OR subject LIKE %s) 
                AND nodeid NOT IN (SELECT nodeid FROM posted_images) AND NOT (date ~ '20[0-9]{2}')
                AND subject NOT LIKE '%Locomotives%' AND subject NOT LIKE '%locomotives%'
                ORDER BY random()
                LIMIT 1
            """
            params = (f"%{term }%", f"%{term }%")

            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
                dict_cur.execute(sql, params)
                return dict_cur.fetchone()
        else:
            sql = """
                SELECT * FROM photos_2024
                WHERE nodeid NOT IN (SELECT nodeid FROM posted_images) AND NOT (date ~ '20[0-9]{2}')
                AND subject NOT LIKE '%Locomotives%' AND subject NOT LIKE '%locomotives%'
                ORDER BY random()
                LIMIT 1
            """
            params = ()

            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
                dict_cur.execute(sql)
                return dict_cur.fetchone()
            
    except Exception as e:
        logging.error(f"Error fetching random photo: {e}")
        return None

def record_posted_image(conn, nodeid):
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO posted_images (nodeid) VALUES (%s)"
            cursor.execute(sql, (nodeid,))
            conn.commit()
            logging.info(f"Inserted nodeid {nodeid} into posted_images")
    except Exception as e:
        logging.error(f"Error inserting nodeid into posted_images: {e}")
        raise