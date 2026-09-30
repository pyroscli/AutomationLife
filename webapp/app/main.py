from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date as date_cls
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from starlette.middleware.sessions import SessionMiddleware

from app.auth import oauth
from app.config import get_settings
from app.db import get_session, init_db
from app.models import DayLog, User

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Daily API", lifespan=lifespan)

# SPA runs on a different origin in dev (Vite :5173), so allow it with cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret, https_only=False)


def current_user(request: Request, session: Session = Depends(get_session)) -> User | None:
    sub = (request.session.get("user") or {}).get("sub")
    if not sub:
        return None
    return session.exec(select(User).where(User.google_sub == sub)).first()


def require_user(user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ---- JSON API (consumed by the TypeScript client) ----------------------------


@app.get("/api/me")
def api_me(user: User | None = Depends(current_user)):
    if not user:
        return {"authenticated": False, "google_configured": settings.google_configured}
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        },
    }


@app.get("/healthz")
def healthz():
    return {"ok": True}


# ---- Daily log (per user, isolated by user_id) -------------------------------


class DayLogIn(BaseModel):
    calories: int | None = None
    steps: int | None = None
    pages: float | None = None
    book: str = ""
    med_morning: bool = False
    med_night: bool = False
    notes: str = ""


def _valid_date(value: str) -> str:
    try:
        return date_cls.fromisoformat(value).isoformat()
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")


def _serialize(day: str, log: DayLog | None) -> dict:
    if log is None:
        return {
            "date": day,
            "saved": False,
            "calories": None,
            "steps": None,
            "pages": None,
            "book": "",
            "med_morning": False,
            "med_night": False,
            "notes": "",
            "updated_at": None,
        }
    return {
        "date": log.date,
        "saved": True,
        "calories": log.calories,
        "steps": log.steps,
        "pages": log.pages,
        "book": log.book,
        "med_morning": log.med_morning,
        "med_night": log.med_night,
        "notes": log.notes,
        "updated_at": log.updated_at.isoformat(),
    }


def _find_day(session: Session, user: User, day: str) -> DayLog | None:
    return session.exec(
        select(DayLog).where(DayLog.user_id == user.id, DayLog.date == day)
    ).first()


@app.get("/api/day/{day}")
def get_day(
    day: str,
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    day = _valid_date(day)
    return _serialize(day, _find_day(session, user, day))


@app.put("/api/day/{day}")
def put_day(
    day: str,
    body: DayLogIn,
    user: User = Depends(require_user),
    session: Session = Depends(get_session),
):
    day = _valid_date(day)
    log = _find_day(session, user, day)
    if log is None:
        log = DayLog(user_id=user.id, date=day)
    log.calories = body.calories
    log.steps = body.steps
    log.pages = body.pages
    log.book = body.book
    log.med_morning = body.med_morning
    log.med_night = body.med_night
    log.notes = body.notes
    log.updated_at = datetime.now(timezone.utc)
    session.add(log)
    session.commit()
    session.refresh(log)
    return _serialize(day, log)


# ---- OAuth (server-side; keeps the Google secret off the browser) ------------


@app.get("/login")
async def login(request: Request):
    if not settings.google_configured:
        return RedirectResponse(settings.frontend_url)
    return await oauth.google.authorize_redirect(request, settings.oauth_redirect_url)


@app.get("/auth/callback")
async def auth_callback(request: Request, session: Session = Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)
    info = token.get("userinfo") or {}
    sub = info.get("sub")
    if not sub:
        return RedirectResponse(settings.frontend_url)

    user = session.exec(select(User).where(User.google_sub == sub)).first()
    if user is None:
        user = User(google_sub=sub)
    user.email = info.get("email", user.email)
    user.name = info.get("name", user.name)
    user.picture = info.get("picture", user.picture)
    session.add(user)
    session.commit()

    request.session["user"] = {"sub": sub}
    return RedirectResponse(settings.frontend_url)


@app.post("/api/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}
