# How to log your day

You do not write the JSON yourself. Run one command from this folder. The script writes `data/days/YYYY-MM-DD.json`. At the end of the month those files become the summary.

Open a terminal in this repo first:

```bash
cd ~/Desktop/ResearchPaper/DailyAutomation
```

---

## How it works

1. GitHub emails you at **8:00** (schedule + morning med) and **21:00** (night med + “log your numbers”).
2. You run `python3 -m daily log ...` with today’s calories, steps, pages, and which meds you took.
3. That creates or updates `data/days/2026-09-13.json` (today’s date in `Asia/Kolkata`).
4. You push that file. On the **1st of next month**, the repo totals calories, steps, pages, and med days into `summaries/YYYY-MM.md` and emails it.

You can run `log` more than once on the same day. New flags overwrite only what you pass. A morning `--med morning` and a night calories command both land in the same file.

---

## Nightly command (copy this)

Replace the numbers and book title:

```bash
python3 -m daily log --calories 2100 --steps 8200 --pages 14 --book "Book title" --med night
```

Then save it to GitHub so the monthly count can see it:

```bash
git add data/days
git commit -m "Log today"
git push
```

---

## Morning med

When you take the morning one:

```bash
python3 -m daily log --med morning
```

You can mark both at night if you forgot earlier:

```bash
python3 -m daily log --calories 2100 --steps 8200 --pages 14 --book "Book title" --med morning --med night
```

---

## If you do not want to type flags

The script asks you one field at a time:

```bash
python3 -m daily log --interactive
```

---

## Check what is already saved

```bash
python3 -m daily today
```

Fix yesterday (or any day) with `--date`:

```bash
python3 -m daily log --date 2026-09-12 --calories 1900 --steps 7000 --pages 8
```

Optional note:

```bash
python3 -m daily log --note "ate out, long walk"
```

---

## Preview / send a reminder yourself

```bash
python3 -m daily remind morning
python3 -m daily remind night
python3 -m daily remind night --send
```

`--send` emails `web3withsingh@gmail.com`. Without it, the text only prints in the terminal.

---

## Month-end summary

Usually GitHub does this on the 1st. To build it locally:

```bash
python3 -m daily summary
python3 -m daily summary --previous
```

That writes `summaries/YYYY-MM.md` with totals, averages, med days, and a day-by-day table.

---

## All commands

| Command | What it does |
|---|---|
| `python3 -m daily today` | Show schedule, meds, and today’s saved numbers |
| `python3 -m daily log --calories N --steps N --pages N --book "…"` | Save tonight’s counts |
| `python3 -m daily log --med morning` | Mark morning med taken |
| `python3 -m daily log --med night` | Mark night med taken |
| `python3 -m daily log --interactive` | Prompt for the fields |
| `python3 -m daily log --date YYYY-MM-DD …` | Edit a past day |
| `python3 -m daily remind morning` / `night` | Print the reminder |
| `python3 -m daily remind night --send` | Email the reminder now |
| `python3 -m daily summary` | Write this month’s markdown summary |

---

## What a day file looks like

After you log, `data/days/2026-09-13.json` is something like:

```json
{
  "date": "2026-09-13",
  "calories": 2100,
  "steps": 8200,
  "pages": 14.0,
  "book": "Book title",
  "meds": {
    "morning": true,
    "night": true
  },
  "notes": "",
  "updated_at": "2026-09-13T21:10:00+05:30"
}
```

Do not put `.env` in git. Only `data/days/` and `summaries/` need to be committed for the counts to survive.
