"""Module for secure audit logging."""
import sqlite3
from datetime import datetime
from encryption import encrypt_data
from logging_config import configure_logging

logger = configure_logging()

def log_audit(action: str, user_id: str, details: str) -> None:
    """Log an audit event to a secure SQLite database.

    Args:
        action: Type of action (e.g., 'analyze_image').
        user_id: Identifier of the user performing the action.
        details: Details of the event.
    """
    try:
        conn = sqlite3.connect("audit_log.db", timeout=5)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit (
                timestamp TEXT,
                action TEXT,
                user_id TEXT,
                details TEXT
            )
        """)
        encrypted_details = encrypt_data(details)
        cursor.execute("INSERT INTO audit VALUES (?, ?, ?, ?)",
                       (datetime.now().isoformat(), action, user_id, encrypted_details))
        conn.commit()
        conn.close()
        logger.info(f"Audit logged: {action} by {user_id}")
    except Exception as e:
        logger.error(f"Audit log error: {e}")