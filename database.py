import psycopg2
from logging_config import configure_logging
logger = configure_logging()
import time
from config import DB_CONFIG  

def connect_to_db(max_retries=3, retry_delay=2):

    retries = 0
    while retries < max_retries:
        try:
            db = psycopg2.connect(
                host=DB_CONFIG["host"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                sslmode=DB_CONFIG["sslmode"]
            )
            logger.info("Successfully connected to the database.")
            return db
        except psycopg2.Error as e:
            retries += 1
            logger.error(f"Failed to connect to database (Attempt {retries}/{max_retries}): {e}")
            if retries < max_retries:
                time.sleep(retry_delay)  
            else:
                logger.error("Max retries reached. Could not connect to the database.")
                return None
