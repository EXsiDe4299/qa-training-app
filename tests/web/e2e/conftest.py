import os
import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn

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
