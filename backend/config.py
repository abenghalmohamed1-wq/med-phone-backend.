"""
config.py — Centralised settings loaded from environment variables / .env
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


# Locate .env — works locally (backend/.env) and on Render (no file needed,
# Render injects real environment variables directly into os.environ).
def _find_env_file() -> str | None:
    candidates = [
        Path("backend/.env"),
        Path(".env"),
        Path("../backend/.env"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


class Settings(BaseSettings):
    # Firebase
    firebase_credentials_path: str = "backend/firebase_credentials.json"
    firebase_project_id: str = ""
    # Realtime Database URL
    firebase_database_url: str = ""

    # Security
    secret_key: str = "change-me"
    cors_origins_raw: str = "http://127.0.0.1:5500,http://localhost:5500,http://localhost:3000"

    # App
    environment: str = "development"
    app_title: str = "Med Phone API"
    app_version: str = "1.0.0"

    # Gemini
    gemini_api_key: str = ""

    model_config = {
        "env_file": _find_env_file(),
        "env_file_encoding": "utf-8",
        "env_prefix": "",
        # Always override with real OS env vars (critical for Render)
        "env_ignore_empty": False,
    }

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]


# Do NOT use lru_cache — it can cache stale empty values before env is loaded.
# FastAPI's Depends() already caches per-request efficiently.
def get_settings() -> Settings:
    return Settings()
