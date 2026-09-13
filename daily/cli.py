from __future__ import annotations

import argparse
import sys
from datetime import date

from daily.config import ROOT, load_config
from daily.mail import send_email
from daily.remind import build_message
from daily.store import load_day, update_day
from daily.summary import previous_month, write_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="daily",
        description="Reminders, daily logs, and monthly summaries.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("today", help="Show today's schedule and current log")

    remind = sub.add_parser("remind", help="Build or send a reminder")
    remind.add_argument("kind", choices=["morning", "night"])
    remind.add_argument("--send", action="store_true", help="Send the reminder by email")

    log = sub.add_parser("log", help="Record tonight's numbers")
    log.add_argument("--date", help="YYYY-MM-DD, defaults to today in your timezone")
    log.add_argument("--calories", type=int)
    log.add_argument("--steps", type=int)
    log.add_argument("--pages", type=float)
    log.add_argument("--book")
    log.add_argument(
        "--med",
        action="append",
        dest="meds",
        choices=["morning", "night"],
        help="Mark a medication as taken. Repeatable.",
    )
    log.add_argument("--note")
    log.add_argument("--interactive", action="store_true", help="Prompt for missing values")

    summary = sub.add_parser("summary", help="Write the monthly markdown summary")
    summary.add_argument("--month", help="YYYY-MM, defaults to the current month")
    summary.add_argument("--previous", action="store_true", help="Use last month")
    summary.add_argument("--send", action="store_true", help="Email the summary")

    args = parser.parse_args(argv)
    config = load_config()

    if args.command == "today":
        return cmd_today(config)
    if args.command == "remind":
        return cmd_remind(config, args.kind, send=args.send)
    if args.command == "log":
        return cmd_log(config, args)
    if args.command == "summary":
        return cmd_summary(config, args)
    parser.error(f"Unknown command: {args.command}")
    return 2


def cmd_today(config) -> int:
    today = config.today()
    log = load_day(today, config)
    print(f"{config.profile.name}  ·  {today.isoformat()}  ·  {config.profile.timezone}")
    print()
    print("Schedule")
    for item in config.schedule:
        print(f"  {item.time}  {item.title}")
    print()
    print("Meds")
    for med in config.meds:
        mark = "taken" if log.meds.get(med.id) else "due"
        print(f"  [{mark}] {med.name} at {med.time}")
    print()
    print("Today's log")
    print(f"  Calories: {_dash(log.calories)}")
    print(f"  Steps:    {_dash(log.steps)}")
    print(f"  Pages:    {_dash(log.pages)}")
    if log.book:
        print(f"  Book:     {log.book}")
    if log.notes:
        print(f"  Notes:    {log.notes}")
    return 0


def cmd_remind(config, kind: str, *, send: bool) -> int:
    subject, body = build_message(kind, config)
    print(subject)
    print()
    print(body, end="")
    if send:
        recipient = send_email(subject, body, to_email=config.profile.email or None)
        print(f"Sent to {recipient}")
    return 0


def cmd_log(config, args) -> int:
    day = date.fromisoformat(args.date) if args.date else config.today()
    calories = args.calories
    steps = args.steps
    pages = args.pages
    book = args.book
    notes = args.note
    meds = list(args.meds or [])

    if args.interactive:
        calories = _ask_int("Calories", calories)
        steps = _ask_int("Steps", steps)
        pages = _ask_float("Pages read", pages)
        book = _ask_str("Book title", book)
        notes = _ask_str("Notes", notes)
        for med in config.meds:
            if med.id in meds:
                continue
            if _ask_yes(f"Did you take {med.name}?", default=False):
                meds.append(med.id)

    if all(value is None for value in (calories, steps, pages, book, notes)) and not meds:
        print("Nothing to log. Pass flags or use --interactive.", file=sys.stderr)
        return 1

    path = update_day(
        day,
        config,
        calories=calories,
        steps=steps,
        pages=pages,
        book=book,
        meds_taken=meds,
        notes=notes,
    )
    log = load_day(day, config)
    print(f"Saved {path.relative_to(ROOT)}")
    print(f"  Calories: {_dash(log.calories)}  Steps: {_dash(log.steps)}  Pages: {_dash(log.pages)}")
    taken = [med_id for med_id, yes in log.meds.items() if yes]
    print(f"  Meds taken: {', '.join(taken) or 'none yet'}")
    return 0


def cmd_summary(config, args) -> int:
    today = config.today()
    if args.previous:
        year, month = previous_month(today)
    elif args.month:
        year_s, month_s = args.month.split("-", 1)
        year, month = int(year_s), int(month_s)
    else:
        year, month = today.year, today.month

    if args.send:
        subject, text = write_summary(year, month, config)
        print(text, end="")
        recipient = send_email(subject, text, to_email=config.profile.email or None)
        print(f"Saved and sent to {recipient}")
        return 0

    _, written = write_summary(year, month, config)
    print(written, end="")
    print(f"Wrote summaries/{year:04d}-{month:02d}.md")
    return 0


def _dash(value) -> str:
    return "—" if value is None else str(value)


def _ask_int(label: str, current: int | None) -> int | None:
    raw = input(f"{label}" + (f" [{current}]" if current is not None else "") + ": ").strip()
    if raw == "":
        return current
    return int(raw)


def _ask_float(label: str, current: float | None) -> float | None:
    raw = input(f"{label}" + (f" [{current}]" if current is not None else "") + ": ").strip()
    if raw == "":
        return current
    return float(raw)


def _ask_str(label: str, current: str | None) -> str | None:
    raw = input(f"{label}" + (f" [{current}]" if current else "") + ": ").strip()
    if raw == "":
        return current
    return raw


def _ask_yes(label: str, *, default: bool) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = input(f"{label} [{hint}]: ").strip().lower()
    if raw == "":
        return default
    return raw in {"y", "yes"}
