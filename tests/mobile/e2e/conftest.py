import os
import socket
import threading
import time
from collections.abc import Generator
from pathlib import Path

import pytest
import uvicorn
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.webdriver import WebDriver

from qa_training_app.db import init_db, reset_db
from qa_training_app.main import app

APPIUM_SERVER = os.getenv("APPIUM_SERVER", "http://127.0.0.1:4723")
APP_ID = "com.example.qatrainingapp"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    init_db()

    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
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

    yield "http://10.0.2.2:8000"

    server.should_exit = True
    thread.join(timeout=5)

    db_path = Path(os.environ["DATABASE"])

    if db_path.exists():
        db_path.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def clean_database(live_server: str):
    reset_db()
    yield


@pytest.fixture
def driver() -> Generator[WebDriver]:
    capabilities = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "Android",
        "appPackage": APP_ID,
        "appActivity": ".MainActivity",
        "noReset": False,
        "newCommandTimeout": 120,
    }

    options = UiAutomator2Options().load_capabilities(capabilities)

    driver = webdriver.Remote(
        APPIUM_SERVER,
        options=options,
    )

    yield driver

    driver.quit()
