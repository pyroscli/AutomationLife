# Daily Automation

A small local agent for daily schedule + medication reminders, a git-backed habit ledger, and a month-end summary

Each night you log calories, steps, and pages. Those files live in this repo so you can count them later.

## What you need

| Piece | Why | Status |
|---|---|---|
| This repo | Schedule, meds, daily counts, monthly summaries | Created here |
| Python 3.11+ | Runs the agent. No extra packages. | Already on macOS |
| Gmail | Sends the reminder and summary emails | You already have Gmail in Cursor |
| Gmail App Password | Lets GitHub or your Mac send mail | [Create one](https://myaccount.google.com/apppasswords) |
| GitHub repo | Runs reminders even when your laptop is closed | Create and push this folder |
| Optional: this Mac | Local 8:00 / 21:00 jobs if you skip GitHub | Only fires if the Mac is awake |

You do **not** need Slack, Twilio, Apple Health, or a calorie app to start. Type the three nightly numbers yourself.

## Daily loop

1. **08:00** — email with today's schedule and the morning med reminder
2. **21:00** — email with the night med reminder and a prompt to log calories / steps / pages
3. **You log** those numbers into `data/days/YYYY-MM-DD.json`
4. **1st of next month** — markdown summary in `summaries/` plus an email

## Setup

1. Put your real email, med names, and schedule in `config.toml`.
2. Copy `.env.example` to `.env` and add a Gmail App Password.
3. Preview a reminder without sending:

```bash
python3 -m daily today
python3 -m daily remind morning
python3 -m daily remind night
```

4. Send one now (needs `.env`):

```bash
python3 -m daily remind morning --send
```

### Reminders when the laptop is off (recommended)

1. Create a GitHub repository and push this folder.
2. In the repo: **Settings → Secrets and variables → Actions**, add:
   - `GMAIL_ADDRESS`
   - `GMAIL_APP_PASSWORD`
   - `TO_EMAIL`
3. GitHub Actions will email you at 08:00 and 21:00 IST, and email + commit the previous month's summary on the 1st.

### Reminders only on this Mac

```bash
chmod +x scripts/install-macos-reminders.sh
./scripts/install-macos-reminders.sh
```

## Nightly log

Full copy-paste guide: [HOW-TO-LOG.md](HOW-TO-LOG.md).

```bash
python3 -m daily log --calories 2100 --steps 8200 --pages 14 --book "Deep Work" --med night
```

Or answer prompts:

```bash
python3 -m daily log --interactive
```

Mark the morning med when you take it:

```bash
python3 -m daily log --med morning
```

Then commit the new day file so the monthly job can see it:

```bash
git add data/days summaries
git commit -m "Log today"
git push
```

## Monthly summary

```bash
python3 -m daily summary
python3 -m daily summary --previous --send
```

Writes `summaries/YYYY-MM.md` with totals, averages, med adherence, and a day-by-day table.

## Change times or meds

Edit `config.toml`. If you change 08:00 / 21:00, also update the cron times in `.github/workflows/daily-reminders.yml` (those are UTC: 08:00 IST = 02:30 UTC, 21:00 IST = 15:30 UTC).
