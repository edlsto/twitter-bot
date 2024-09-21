import psycopg2.extras
import logging

logging.basicConfig(level=logging.INFO)

def get_random_photo(conn, term=None):
    try:
        if term:
            sql = """
                SELECT * FROM photos_2024 
                WHERE (summary LIKE %s OR subject LIKE %s)
                ORDER BY random()
                LIMIT 1
            """
            params = (f"%{term}%", f"%{term}%")
        else:
            sql = """
                SELECT * FROM photos_2024
                ORDER BY random()
                LIMIT 1
            """
            params = ()

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
            logging.info("Executing SQL query: %s", sql)
            dict_cur.execute(sql, params)
            return dict_cur.fetchone()
            
    except Exception as e:
        logging.error(f"Error fetching random photo: {e}")
        return None