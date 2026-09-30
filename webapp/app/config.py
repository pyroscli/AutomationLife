from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load webapp/.env if present. Real env vars (e.g. on Render) win over the file.
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH, override=False)

# Default dev database: a local SQLite file so the app boots with zero setup.
_DEFAULT_SQLITE = f"sqlite:///{Path(__file__).resolve().parent.parent / 'webapp.db'}"


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.environ.get("DATABASE_URL") or _DEFAULT_SQLITE
        self.session_secret: str = os.environ.get("SESSION_SECRET", "dev-insecure-secret")
        self.google_client_id: str = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        self.google_client_secret: str = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
        self.base_url: str = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")
        # Where the TypeScript SPA runs; login redirects back here and CORS allows it.
        self.frontend_url: str = os.environ.get("FRONTEND_URL", "http://localhost:5173").rstrip("/")
        # OAuth callback URL registered in Google. In dev the Vite proxy serves it
        # from the frontend origin so the session cookie stays same-origin.
        self.oauth_redirect_url: str = (
            os.environ.get("OAUTH_REDIRECT_URL") or f"{self.frontend_url}/auth/callback"
        )

    @property
    def google_configured(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)


@lru_cache
def get_settings() -> Settings:
    return Settings()
