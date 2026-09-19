# How to log your day

You do not write the JSON yourself. Run one command from this folder. That **one command** does both jobs: it writes `data/days/YYYY-MM-DD.json` **and** appends the same day to the Google Sheet. At the end of the month the JSON files become the markdown summary; the sheet is the running month view.

Open a terminal in this repo first:

```bash
cd ~/Desktop/ResearchPaper/DailyAutomation
```

---

## How it works

1. GitHub emails you at **8:00** (schedule + morning med) and **21:00** (night med + “log your numbers”).
2. You run **one** `python3 -m daily log ...` with today’s calories, steps, pages, and which meds you took.
3. That creates or updates `data/days/YYYY-MM-DD.json` (today’s date in `Asia/Kolkata`).
4. The same command immediately POSTs that day to Activepieces, which **Add Row**s it in **Daily Routine → Sheet1**.
5. You push the JSON file. On the **1st of next month**, the repo totals calories, steps, pages, and med days into `summaries/YYYY-MM.md` and emails it.

You can run `log` more than once on the same day. New flags overwrite only what you pass **in the JSON**. A morning `--med morning` and a night calories command both land in the same file. The sheet **appends a new row each time**, so log the full night numbers once when you can. If a day is out of order, sort the sheet by column A (date).

---

## Nightly command (JSON + sheet together)

This is the joint step. Replace the numbers and book title. Do not run a separate sheet command afterward.

```bash
python3 -m daily log --calories 2100 --steps 8200 --pages 14 --book "Book title" --med night
```

You should see both lines:

```
Saved data/days/2026-09-19.json
Sheet synced for 2026-09-19
```

Then save the JSON to GitHub so the monthly count can see it:

```bash
git add data/days
git commit -m "Log today"
git push
```

JSON-only (skip the sheet):

```bash
python3 -m daily log --calories 2100 --steps 8200 --pages 14 --book "Book title" --med night --no-sheet
```

Sheet-only (JSON already saved, backfill a day or a month):

```bash
python3 -m daily sheet --date 2026-09-13
python3 -m daily sheet --month 2026-09
```

---

## Morning med

When you take the morning one:

```bash
python3 -m daily log --med morning
```

That also appends a sheet row (often incomplete until night). Prefer marking morning med in the **same** night `log` as the calories/steps/pages:

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

## Google Sheet (Activepieces)

The JSON files stay the source of truth. Activepieces only appends a row to [Daily Routine](https://docs.google.com/spreadsheets/d/1dcg0Bb0MazjpwVOdmjqm_Z3FHbKqaPrqLGcWBo-oVC4/edit) after a successful `log`.

Published flow (already set up):

1. **Trigger:** Catch Webhook. Live URL in `.env` as `ACTIVEPIECES_WEBHOOK_URL` (not `/test`).
2. **Action:** Google Sheets → **Add Row** (not Find or Create).
3. Spreadsheet **Daily Routine**, tab **Sheet1**.
4. **First Row Contains Headers** = on.
5. Header row in the sheet:

```
date	calories	steps	pages	book	med_morning	med_night	notes	updated_at
```

6. One purple Catch Webhook chip per column: `body date`, `body calories`, `body steps`, `body pages`, `body book`, `body med_morning`, `body med_night`, `body notes`, `body updated_at`. Authentication stays **None**.

`log` is the joint write. `sheet` is only for backfill. After a night log, sort column A if you want dates in order.

---

## All commands

| Command | What it does |
|---|---|
| `python3 -m daily today` | Show schedule, meds, and today’s saved numbers |
| `python3 -m daily log --calories N --steps N --pages N --book "…"` | Save JSON **and** append the Google Sheet row |
| `python3 -m daily log --med morning` | Mark morning med taken (JSON + sheet) |
| `python3 -m daily log --med night` | Mark night med taken (JSON + sheet) |
| `python3 -m daily log --interactive` | Prompt for the fields, then JSON + sheet |
| `python3 -m daily log --date YYYY-MM-DD …` | Edit a past day (JSON + sheet) |
| `python3 -m daily log … --no-sheet` | JSON only |
| `python3 -m daily remind morning` / `night` | Print the reminder |
| `python3 -m daily remind night --send` | Email the reminder now |
| `python3 -m daily sheet` | Push today to the sheet (backfill) |
| `python3 -m daily sheet --month YYYY-MM` | Push every saved day in that month |
| `python3 -m daily sheet --sample` | Print the JSON Activepieces should receive |
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
