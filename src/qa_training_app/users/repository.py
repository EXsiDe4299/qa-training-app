import sqlite3

from qa_training_app.users.interfaces import UserRepositoryABC
from qa_training_app.users.schemas import User


class UserRepository(UserRepositoryABC):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get_by_id(self, user_id: int) -> User | None:
        row = self.connection.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
        )

    def get_by_username(self, username: str) -> User | None:
        row = self.connection.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if row is None:
            return None

        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
        )

    def create(
        self,
        username: str,
        password_hash: str,
    ) -> User:
        cursor = self.connection.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash),
        )

        self.connection.commit()

        user_id = cursor.lastrowid

        if user_id is None:
            raise RuntimeError("User ID was not returned after creation")

        return User(
            id=user_id,
            username=username,
            password_hash=password_hash,
        )
