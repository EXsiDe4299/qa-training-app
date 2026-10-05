import sqlite3
from contextlib import contextmanager

from qa_training_app.config import settings


@contextmanager
def get_db():
    connection = sqlite3.connect(settings.database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
    finally:
        connection.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
            """)

        conn.commit()


def reset_db() -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM requests")
        conn.execute("DELETE FROM users")
        conn.commit()
