from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from app.config import get_settings

_settings = get_settings()

oauth = OAuth()

# Google's OpenID Connect discovery doc wires up all endpoints automatically.
# Identity-only scopes: no Sheets/Drive access, so no Google verification fees.
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=_settings.google_client_id or None,
    client_secret=_settings.google_client_secret or None,
    client_kwargs={"scope": "openid email profile"},
)
