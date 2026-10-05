import os
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
os.environ.setdefault("DATABASE", str(TEST_DIR / ".test.db"))
os.environ.setdefault("SESSION_SECRET", "test-secret")
