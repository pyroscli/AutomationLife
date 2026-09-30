from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # Google's stable unique user id (the OIDC "sub" claim).
    google_sub: str = Field(index=True, unique=True)
    email: str = Field(index=True)
    name: str = ""
    picture: str = ""
    created_at: datetime = Field(default_factory=_utcnow)


class DayLog(SQLModel, table=True):
    """One row per user per day. Filled in during step 2."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    date: str = Field(index=True)  # YYYY-MM-DD in the user's timezone
    calories: int | None = None
    steps: int | None = None
    pages: float | None = None
    book: str = ""
    med_morning: bool = False
    med_night: bool = False
    notes: str = ""
    updated_at: datetime = Field(default_factory=_utcnow)
