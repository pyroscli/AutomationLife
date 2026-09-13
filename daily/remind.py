from __future__ import annotations

from daily.config import Config
from daily.store import load_day


def morning_message(config: Config) -> tuple[str, str]:
    today = config.today()
    log = load_day(today, config)
    morning_meds = [med for med in config.meds if med.id == "morning"]
    schedule_lines = "\n".join(f"- {item.time}  {item.title}" for item in config.schedule) or "- (add items in config.toml)"
    med_lines = "\n".join(
        f"- {med.name} at {med.time}" + (f" — {med.note}" if med.note else "")
        for med in morning_meds
    ) or "- (add a morning med in config.toml)"

    yesterday = load_day(today.fromordinal(today.toordinal() - 1), config)
    yesterday_bits = []
    if yesterday.calories is not None:
        yesterday_bits.append(f"{yesterday.calories} kcal")
    if yesterday.steps is not None:
        yesterday_bits.append(f"{yesterday.steps} steps")
    if yesterday.pages is not None:
        yesterday_bits.append(f"{yesterday.pages} pages")
    yesterday_line = ", ".join(yesterday_bits) if yesterday_bits else "nothing logged yet"

    body = f"""Good morning, {config.profile.name}.

Today is {today.isoformat()}.

Morning medication
{med_lines}

Today's schedule
{schedule_lines}

Yesterday: {yesterday_line}

Tonight you will log calories, steps, and pages read:
  python3 -m daily log --calories 2000 --steps 8000 --pages 12
"""
    if log.meds.get("morning"):
        body += "\nMorning med is already marked taken for today.\n"
    return f"Morning plan — {today.isoformat()}", body.strip() + "\n"


def night_message(config: Config) -> tuple[str, str]:
    today = config.today()
    log = load_day(today, config)
    night_meds = [med for med in config.meds if med.id == "night"]
    med_lines = "\n".join(
        f"- {med.name} at {med.time}" + (f" — {med.note}" if med.note else "")
        for med in night_meds
    ) or "- (add a night med in config.toml)"

    logged = []
    logged.append(f"Calories: {log.calories if log.calories is not None else 'not logged'}")
    logged.append(f"Steps: {log.steps if log.steps is not None else 'not logged'}")
    logged.append(f"Pages: {log.pages if log.pages is not None else 'not logged'}")
    if log.book:
        logged.append(f"Book: {log.book}")

    body = f"""Good evening, {config.profile.name}.

Today is {today.isoformat()}.

Night medication
{med_lines}

Log tonight's numbers before you sleep
{chr(10).join(f'- {line}' for line in logged)}

Commands:
  python3 -m daily log --calories 2000 --steps 8000 --pages 12 --book "Book title"
  python3 -m daily log --med night
  python3 -m daily log --interactive
"""
    return f"Night wrap-up — {today.isoformat()}", body.strip() + "\n"


def build_message(kind: str, config: Config) -> tuple[str, str]:
    if kind == "morning":
        return morning_message(config)
    if kind == "night":
        return night_message(config)
    raise ValueError(f"Unknown reminder kind: {kind}")
