from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.toml"
DATA_DIR = ROOT / "data" / "days"
SUMMARIES_DIR = ROOT / "summaries"
ENV_PATH = ROOT / ".env"


@dataclass(frozen=True)
class Profile:
    name: str
    timezone: str
    email: str

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


@dataclass(frozen=True)
class Med:
    id: str
    name: str
    time: str
    note: str = ""


@dataclass(frozen=True)
class ScheduleItem:
    time: str
    title: str


@dataclass(frozen=True)
class Config:
    profile: Profile
    morning: str
    night: str
    meds: list[Med]
    schedule: list[ScheduleItem]

    def now(self) -> datetime:
        return datetime.now(self.profile.tz)

    def today(self):
        return self.now().date()

    def med(self, med_id: str) -> Med | None:
        for med in self.meds:
            if med.id == med_id:
                return med
        return None


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_PATH.exists():
        return values
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_config(path: Path = CONFIG_PATH) -> Config:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")

    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    profile_raw = raw.get("profile", {})
    reminders = raw.get("reminders", {})

    profile = Profile(
        name=str(profile_raw.get("name", "Friend")),
        timezone=str(profile_raw.get("timezone", "Asia/Kolkata")),
        email=str(profile_raw.get("email", "")),
    )
    meds = [
        Med(
            id=str(item.get("id", "")),
            name=str(item.get("name", "Medication")),
            time=str(item.get("time", "")),
            note=str(item.get("note", "")),
        )
        for item in raw.get("meds", [])
    ]
    schedule = [
        ScheduleItem(time=str(item.get("time", "")), title=str(item.get("title", "")))
        for item in raw.get("schedule", [])
    ]
    return Config(
        profile=profile,
        morning=str(reminders.get("morning", "08:00")),
        night=str(reminders.get("night", "21:00")),
        meds=meds,
        schedule=schedule,
    )
