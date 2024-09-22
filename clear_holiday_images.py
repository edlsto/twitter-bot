import psycopg2
import os

def clear_holiday_images(connection):
    try:
        with connection.cursor() as cursor:
            # Delete holiday images from posted_images based on shared_photos
            delete_sql = """
                DELETE FROM posted_images 
                WHERE nodeid IN (
                    SELECT nodeid FROM shared_photos 
                    WHERE subject LIKE '%Christmas%' 
                       OR subject LIKE '%Halloween%' 
                       OR subject LIKE '%New Year%' 
                       OR subject LIKE '%Easter%' 
                       OR subject LIKE '%Thanksgiving%' 
                       OR subject LIKE '%Fourth of July%' 
                       OR summary LIKE '%Christmas%' 
                       OR summary LIKE '%Halloween%' 
                       OR summary LIKE '%New Year%' 
                       OR summary LIKE '%Easter%' 
                       OR summary LIKE '%Thanksgiving%' 
                       OR summary LIKE '%Fourth of July%' 
                );
            """
            cursor.execute(delete_sql)
            connection.commit()
            print("Holiday images cleared from posted_images successfully.")
    except Exception as e:
        print(f"Error clearing holiday images: {e}")
        connection.rollback()

def main():
    # Database connection details
    conn_string = os.getenv("DATABASE_URL")  # Use environment variable for DB URL
    try:
        with psycopg2.connect(conn_string) as conn:
            clear_holiday_images(conn)
    except Exception as e:
        print(f"Could not connect to the database: {e}")

if __name__ == "__main__":
    main()
