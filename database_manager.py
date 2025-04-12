"""Module for managing secure database connections and queries."""
import psycopg2
import sqlite3
import os, time
from dotenv import load_dotenv
from logging_config import configure_logging
from encryption import encrypt_data, decrypt_data

logger = configure_logging()
load_dotenv()

def connect_to_db(max_retries: int = 3, retry_delay: int = 2) -> psycopg2.extensions.connection:
    """Connect to PostgreSQL database with SSL.

    Args:
        max_retries: Maximum connection attempts.
        retry_delay: Delay between retries in seconds.

    Returns:
        Database connection object or None if failed.
    """
    retries = 0
    while retries < max_retries:
        try:
            db = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "MilitaryDB"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                sslmode="verify-full",
                sslrootcert=os.getenv("SSL_ROOT_CERT_PATH"),
                options="-c statement_timeout=500"
            )
            db.set_session(readonly=False, autocommit=False)
            logger.info("Connected to database securely")
            return db
        except psycopg2.Error as e:
            retries += 1
            logger.error(f"Database connection failed (Attempt {retries}/{max_retries}): {e}")
            if retries < max_retries:
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached")
                return None

def init_offline_db() -> sqlite3.Connection:
    """Initialize SQLite database for offline mode.

    Returns:
        SQLite connection object or None if failed.
    """
    try:
        conn = sqlite3.connect("offline_cache.db", timeout=5)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS offline_wanted (
                id INTEGER PRIMARY KEY,
                face_encoding TEXT,
                name TEXT,
                age INTEGER,
                nationality TEXT,
                crime TEXT,
                danger_level TEXT
            )
        """)
        conn.commit()
        return conn
    except Exception as e:
        logger.error(f"Offline DB init error: {e}")
        return None

def search_database(db: psycopg2.extensions.connection, face_encoding: str, offline_mode: bool = False) -> tuple:
    """Search database for a matching face encoding.

    Args:
        db: Database connection (None if offline).
        face_encoding: Encrypted face encoding string.
        offline_mode: Whether to use offline SQLite database.

    Returns:
        Tuple of (name, age, nationality, crime, danger_level) or None.
    """
    if offline_mode:
        try:
            conn = init_offline_db()
            if not conn:
                return None
            cursor = conn.cursor()
            cursor.execute("SELECT name, age, nationality, crime, danger_level FROM offline_wanted WHERE face_encoding = ?", (face_encoding,))
            result = cursor.fetchone()
            conn.close()
            if result:
                logger.info(f"Offline match: {result[0]}")
                return result
            return None
        except Exception as e:
            logger.error(f"Offline search error: {e}")
            return None
    else:
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT name, age, nationality, crime, danger_level FROM wanted_individuals WHERE face_encoding = %s", (face_encoding,))
                result = cursor.fetchone()
                if result:
                    logger.info(f"Online match: {result[0]}")
                    return result
                return None
        except Exception as e:
            logger.error(f"Online search error: {e}")
            return None