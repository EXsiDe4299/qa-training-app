import sqlite3

from qa_training_app.requests.interfaces import RequestRepositoryABC
from qa_training_app.requests.schemas import RequestItem


class RequestRepository(RequestRepositoryABC):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get_all(self) -> list[RequestItem]:
        rows = self.connection.execute("""
            SELECT
                requests.id,
                requests.title,
                requests.description,
                requests.author_id,
                users.username AS author_username
            FROM requests
            JOIN users
                ON users.id = requests.author_id
            ORDER BY requests.id DESC
            """).fetchall()

        return [
            RequestItem(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                author_id=row["author_id"],
                author_username=row["author_username"],
            )
            for row in rows
        ]

    def get_by_id(
        self,
        request_id: int,
    ) -> RequestItem | None:
        row = self.connection.execute(
            """
            SELECT
                requests.id,
                requests.title,
                requests.description,
                requests.author_id,
                users.username AS author_username
            FROM requests
            JOIN users
                ON users.id = requests.author_id
            WHERE requests.id = ?
            """,
            (request_id,),
        ).fetchone()

        if row is None:
            return None

        return RequestItem(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            author_id=row["author_id"],
            author_username=row["author_username"],
        )

    def create(
        self,
        title: str,
        description: str,
        author_id: int,
    ) -> RequestItem:
        cursor = self.connection.execute(
            """
            INSERT INTO requests (
                title,
                description,
                author_id
            )
            VALUES (?, ?, ?)
            """,
            (
                title,
                description,
                author_id,
            ),
        )

        self.connection.commit()

        request_id = cursor.lastrowid

        if request_id is None:
            raise RuntimeError("Request ID was not returned after creation")

        request = self.get_by_id(request_id)

        if request is None:
            raise RuntimeError("Request was not created")

        return request

    def delete(self, request_id: int) -> None:
        self.connection.execute(
            """
            DELETE FROM requests
            WHERE id = ?
            """,
            (request_id,),
        )

        self.connection.commit()
