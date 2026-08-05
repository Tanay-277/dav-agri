from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Backend root: <project>/backend
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")


class Settings:
    """Application settings loaded from environment / .env file."""

    # --- Core ---
    APP_NAME: str = os.getenv("APP_NAME", "AgriStory Analytics API")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"}
    ENV: str = os.getenv("ENV", "development")

    # --- Server ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if o.strip()
    ]

    # --- Data ---
    DATASET_DIR: Path = PROJECT_DIR / "dataset"
    DATASET_FILE: str = os.getenv("DATASET_FILE", "agriculture.csv")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///agri.db")

    # --- AI (Gemini) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "true").lower() in {
        "1",
        "true",
        "yes",
    }

    # --- Export ---
    EXPORT_DIR: Path = BACKEND_DIR / "exports"

    # --- Derived ---
    @property
    def dataset_path(self) -> Path:
        return self.DATASET_DIR / self.DATASET_FILE

    def __post_init__(self) -> None:  # pragma: no cover
        self.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        self.DATASET_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
