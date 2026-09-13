from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

from daily.config import load_env


def resolve_mail_settings() -> dict[str, str]:
    env = {**load_env(), **os.environ}
    return {
        "address": env.get("GMAIL_ADDRESS", "").strip(),
        "password": env.get("GMAIL_APP_PASSWORD", "").strip().replace(" ", ""),
        "to": env.get("TO_EMAIL", "").strip(),
        "smtp_host": env.get("SMTP_HOST", "smtp.gmail.com").strip(),
        "smtp_port": env.get("SMTP_PORT", "587").strip(),
    }


def send_email(subject: str, body: str, *, to_email: str | None = None) -> str:
    settings = resolve_mail_settings()
    sender = settings["address"]
    password = settings["password"]
    recipient = to_email or settings["to"] or sender

    if not sender or not password or not recipient:
        raise RuntimeError(
            "Email is not configured. Set GMAIL_ADDRESS, GMAIL_APP_PASSWORD, and TO_EMAIL "
            "in .env or as environment variables."
        )

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings["smtp_host"], int(settings["smtp_port"])) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(message)

    return recipient
