from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database: str = "app.db"
    session_secret: str

    base_dir: ClassVar[Path] = Path(__file__).resolve().parent

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # pyright: ignore
