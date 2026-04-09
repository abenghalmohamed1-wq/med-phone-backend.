"""
config.py — Centralised settings loaded from .env
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # Firebase
    firebase_credentials_path: str = "backend/firebase_credentials.json"
    firebase_project_id: str = ""
    # Realtime Database URL — format: https://<project-id>-default-rtdb.firebaseio.com
    firebase_database_url: str = ""

    # Security
    secret_key: str = "change-me"
    # Stored as a raw comma-separated string; use .allowed_origins for a list
    cors_origins_raw: str = (
        "http://127.0.0.1:5500,http://localhost:5500,http://localhost:3000"
    )

    # App
    environment: str = "development"
    app_title: str = "Med Phone API"
    app_version: str = "1.0.0"

    model_config = {
        "env_file": "backend/.env",
        "env_file_encoding": "utf-8",
        "env_prefix": "",
    }

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
