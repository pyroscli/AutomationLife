from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path

from daily.config import DATA_DIR, SUMMARIES_DIR, Config


@dataclass
class DayLog:
    date: str
    calories: int | None = None
    steps: int | None = None
    pages: float | None = None
    book: str = ""
    meds: dict[str, bool] = field(default_factory=dict)
    notes: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def day_path(day: date) -> Path:
    return DATA_DIR / f"{day.isoformat()}.json"


def empty_log(day: date, med_ids: list[str]) -> DayLog:
    return DayLog(
        date=day.isoformat(),
        meds={med_id: False for med_id in med_ids},
    )


def load_day(day: date, config: Config) -> DayLog:
    path = day_path(day)
    med_ids = [med.id for med in config.meds]
    if not path.exists():
        return empty_log(day, med_ids)

    raw = json.loads(path.read_text(encoding="utf-8"))
    meds = {med_id: False for med_id in med_ids}
    meds.update({str(k): bool(v) for k, v in raw.get("meds", {}).items()})
    return DayLog(
        date=str(raw.get("date", day.isoformat())),
        calories=_maybe_int(raw.get("calories")),
        steps=_maybe_int(raw.get("steps")),
        pages=_maybe_float(raw.get("pages")),
        book=str(raw.get("book", "")),
        meds=meds,
        notes=str(raw.get("notes", "")),
        updated_at=str(raw.get("updated_at", "")),
    )


def save_day(log: DayLog, now: datetime) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    log.updated_at = now.isoformat(timespec="seconds")
    path = day_path(date.fromisoformat(log.date))
    path.write_text(json.dumps(log.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def update_day(
    day: date,
    config: Config,
    *,
    calories: int | None = None,
    steps: int | None = None,
    pages: float | None = None,
    book: str | None = None,
    meds_taken: list[str] | None = None,
    notes: str | None = None,
) -> Path:
    log = load_day(day, config)
    if calories is not None:
        log.calories = calories
    if steps is not None:
        log.steps = steps
    if pages is not None:
        log.pages = pages
    if book is not None:
        log.book = book
    if notes is not None:
        log.notes = notes
    for med_id in meds_taken or []:
        if med_id not in log.meds:
            raise ValueError(f"Unknown med id: {med_id}. Known: {', '.join(log.meds) or '(none)'}")
        log.meds[med_id] = True
    return save_day(log, config.now())


def list_month(year: int, month: int, config: Config) -> list[DayLog]:
    logs: list[DayLog] = []
    prefix = f"{year:04d}-{month:02d}-"
    if not DATA_DIR.exists():
        return logs
    for path in sorted(DATA_DIR.glob(f"{prefix}*.json")):
        day = date.fromisoformat(path.stem)
        logs.append(load_day(day, config))
    return logs


def summary_path(year: int, month: int) -> Path:
    return SUMMARIES_DIR / f"{year:04d}-{month:02d}.md"


def _maybe_int(value) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _maybe_float(value) -> float | None:
    if value in (None, ""):
        return None
    return float(value)
