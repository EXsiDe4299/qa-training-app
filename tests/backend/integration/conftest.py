import os
import socket
import sqlite3
import threading
import time
from collections.abc import Callable
from pathlib import Path

import bcrypt
import pytest
import requests
import uvicorn

from qa_training_app.config import settings
from qa_training_app.db import init_db, reset_db
from qa_training_app.main import app


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    init_db()

    port = _free_port()

    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )

    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    timeout = time.time() + 10

    while not server.started:
        if time.time() > timeout:
            raise RuntimeError("Test server did not start")

        time.sleep(0.05)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)

    db_path = Path(os.environ["DATABASE"])

    if db_path.exists():
        db_path.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def base_url(live_server: str):
    return live_server


@pytest.fixture(autouse=True)
def clean_database(live_server: str):
    reset_db()
    yield


@pytest.fixture
def connection():
    connection = sqlite3.connect(settings.database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture
def create_user(
    connection: sqlite3.Connection,
) -> Callable[[str, str], sqlite3.Row]:
    def _create_user(username: str, password: str) -> sqlite3.Row:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        cursor = connection.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash),
        )
        connection.commit()

        return connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return _create_user


@pytest.fixture
def authenticated_session(
    base_url: str,
) -> Callable[[str, str], requests.Session]:
    def _authenticated_session(
        username: str,
        password: str,
    ) -> requests.Session:
        session = requests.Session()

        response = session.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )

        assert response.status_code == 200
        assert "session" in session.cookies

        return session

    return _authenticated_session


@pytest.fixture
def create_request(
    connection: sqlite3.Connection,
) -> Callable[[str, str, int], sqlite3.Row]:
    def _create_request(
        title: str,
        description: str,
        author_id: int,
    ) -> sqlite3.Row:
        cursor = connection.execute(
            """
            INSERT INTO requests (
                title,
                description,
                author_id
            )
            VALUES (?, ?, ?)
            """,
            (title, description, author_id),
        )
        connection.commit()

        return connection.execute(
            "SELECT * FROM requests WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return _create_request
