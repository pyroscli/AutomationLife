from __future__ import annotations

from calendar import monthrange
from datetime import date

from daily.config import Config, SUMMARIES_DIR
from daily.store import DayLog, list_month, summary_path


def previous_month(day: date) -> tuple[int, int]:
    if day.month == 1:
        return day.year - 1, 12
    return day.year, day.month - 1


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _fmt(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "—"
    if digits == 0:
        return f"{int(round(value)):,}"
    return f"{value:.{digits}f}"


def build_summary(year: int, month: int, config: Config) -> str:
    logs = list_month(year, month, config)
    days_in_month = monthrange(year, month)[1]
    month_label = date(year, month, 1).strftime("%B %Y")

    calories = [float(log.calories) for log in logs if log.calories is not None]
    steps = [float(log.steps) for log in logs if log.steps is not None]
    pages = [float(log.pages) for log in logs if log.pages is not None]
    books = sorted({log.book for log in logs if log.book})

    med_lines = []
    for med in config.meds:
        taken = sum(1 for log in logs if log.meds.get(med.id))
        med_lines.append(f"| {med.name} | {taken} / {days_in_month} |")

    rows = [_row(log, config) for log in logs] or ["| — | — | — | — | — |"]

    text = f"""# {month_label}

Days with a log: **{len(logs)} / {days_in_month}**

## Totals

| Metric | Days logged | Total | Daily average |
|---|---:|---:|---:|
| Calories | {len(calories)} | {_fmt(sum(calories) if calories else None)} | {_fmt(_avg(calories))} |
| Steps | {len(steps)} | {_fmt(sum(steps) if steps else None)} | {_fmt(_avg(steps))} |
| Pages read | {len(pages)} | {_fmt(sum(pages) if pages else None, 1)} | {_fmt(_avg(pages), 1)} |

## Medications

| Med | Taken |
|---|---:|
{chr(10).join(med_lines) if med_lines else "| — | — |"}

## Books

{chr(10).join(f"- {book}" for book in books) or "- (no book titles logged)"}

## Daily log

| Date | Calories | Steps | Pages | Meds |
|---|---:|---:|---:|---|
{chr(10).join(rows)}
"""
    return text.strip() + "\n"


def write_summary(year: int, month: int, config: Config) -> tuple[str, str]:
    text = build_summary(year, month, config)
    path = summary_path(year, month)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    subject = f"Monthly summary — {date(year, month, 1).strftime('%B %Y')}"
    return subject, text


def _row(log: DayLog, config: Config) -> str:
    meds = ", ".join(
        f"{med.id}:{'yes' if log.meds.get(med.id) else 'no'}" for med in config.meds
    ) or "—"
    return (
        f"| {log.date} | "
        f"{log.calories if log.calories is not None else '—'} | "
        f"{log.steps if log.steps is not None else '—'} | "
        f"{log.pages if log.pages is not None else '—'} | "
        f"{meds} |"
    )
