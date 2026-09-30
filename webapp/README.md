# Daily — web app

Mobile-first, multi-user rebuild of the `daily` CLI. Sign in with Google,
log your day, see a dashboard, get reminders.

- **Backend** (`app/`) — FastAPI JSON API + Google OAuth. Data per user in
  Postgres (SQLite locally for dev).
- **Client** (`client/`) — Vite + React + TypeScript SPA.

## Run locally (two processes)

Backend:

```bash
cd webapp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # set SESSION_SECRET; add Google IDs to enable login
uvicorn app.main:app --reload --port 8000
```

Client (separate terminal):

```bash
cd webapp/client
npm install
npm run dev
```

Open **http://localhost:5173**. Vite proxies `/api`, `/login`, `/auth` to the
backend on `:8000`, so the whole app is same-origin and cookies just work.
With no Google IDs the page explains what's missing; API and DB still run.

## Env

See `.env.example`. `DATABASE_URL` unset → local SQLite file `webapp.db`.
For Postgres use `postgresql+psycopg://USER:PASS@HOST/DB` (Neon/Supabase free tier).
For local Google login, register the redirect URI as
`http://localhost:5173/auth/callback` (served through the Vite proxy).

## Status

- [x] Step 1 — FastAPI JSON API, Google login, DB, React+TS client (this)
- [ ] Step 2 — daily logging form
- [ ] Step 3 — dashboard + CSV export
- [ ] Step 4 — per-user reminders
- [ ] Step 5 — polish + deploy
