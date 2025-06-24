import sqlite3
import threading
from bot.utils.logger import logger

class UserRegistry:
    def __init__(self, db_path="storage/users.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    telegram_id INTEGER,
                    profile_name TEXT,
                    PRIMARY KEY (telegram_id, profile_name)
                )
            """)
            conn.commit()
        logger.info("Initialized SQLite database.")

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def add_profile(self, telegram_id: int, profile_name: str):
        with self._lock, self._get_conn() as conn:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO user_profiles (telegram_id, profile_name) VALUES (?, ?)",
                    (telegram_id, profile_name)
                )
                conn.commit()
                logger.debug(f"Added profile '{profile_name}' for user {telegram_id}.")
            except Exception as e:
                logger.error(f"Failed to add profile: {e}")

    def remove_profile(self, telegram_id: int, profile_name: str):
        with self._lock, self._get_conn() as conn:
            try:
                conn.execute(
                    "DELETE FROM user_profiles WHERE telegram_id = ? AND profile_name = ?",
                    (telegram_id, profile_name)
                )
                conn.commit()
                logger.debug(f"Removed profile '{profile_name}' for user {telegram_id}.")
            except Exception as e:
                logger.error(f"Failed to remove profile: {e}")

    def get_profiles(self, telegram_id: int):
        with self._lock, self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT profile_name FROM user_profiles WHERE telegram_id = ?",
                (telegram_id,)
            )
            rows = cursor.fetchall()
            return [row[0] for row in rows]
