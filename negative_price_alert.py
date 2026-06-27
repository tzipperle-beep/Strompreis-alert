#!/usr/bin/env python3
"""Sendet eine E-Mail, wenn der Day-Ahead-Strompreis am naechsten Tag negativ ist."""

import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

import requests

ENERGY_CHARTS_URL = "https://api.energy-charts.info/price"

BIDDING_ZONE = os.environ.get("BIDDING_ZONE", "DE-LU")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO")

# Day-Ahead-Preise werden in dieser Zone veroeffentlicht; fuer die Anzeige
# rechnen wir die UTC-Zeitstempel der API in CET/CEST um.
try:
    from zoneinfo import ZoneInfo

    LOCAL_TZ = ZoneInfo("Europe/Berlin")
except ImportError:  # pragma: no cover
    LOCAL_TZ = timezone.utc


def fetch_prices(date_str: str) -> dict:
    response = requests.get(
        ENERGY_CHARTS_URL,
        params={"bzn": BIDDING_ZONE, "start": date_str, "end": date_str},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def find_negative_periods(data: dict) -> list[tuple[datetime, datetime]]:
    timestamps = data.get("unix_seconds", [])
    prices = data.get("price", [])
    if not timestamps or not prices or len(timestamps) != len(prices):
        return []

    # Intervall-Dauer aus den Zeitstempeln ableiten (i.d.R. 1h, teils 15min).
    interval_seconds = timestamps[1] - timestamps[0] if len(timestamps) > 1 else 3600

    periods = []
    block_start = None
    for ts, price in zip(timestamps, prices):
        if price is not None and price < 0:
            if block_start is None:
                block_start = ts
            block_end = ts + interval_seconds
        else:
            if block_start is not None:
                periods.append((block_start, block_end))
                block_start = None
    if block_start is not None:
        periods.append((block_start, block_end))

    return [
        (
            datetime.fromtimestamp(start, tz=timezone.utc).astimezone(LOCAL_TZ),
            datetime.fromtimestamp(end, tz=timezone.utc).astimezone(LOCAL_TZ),
        )
        for start, end in periods
    ]


def build_message(date_str: str, periods: list[tuple[datetime, datetime]]) -> str:
    lines = [f"⚡ Negative Strompreise am {date_str} ({BIDDING_ZONE}):"]
    for start, end in periods:
        lines.append(f"- {start.strftime('%H:%M')} bis {end.strftime('%H:%M')} Uhr")
    return "\n".join(lines)


def send_email(subject: str, body: str) -> None:
    if not SMTP_USER or not SMTP_PASSWORD or not EMAIL_TO:
        raise RuntimeError("SMTP_USER, SMTP_PASSWORD und EMAIL_TO muessen gesetzt sein.")

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = SMTP_USER
    message["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [EMAIL_TO], message.as_string())


def main() -> int:
    tomorrow = datetime.now(LOCAL_TZ).date() + timedelta(days=1)
    date_str = tomorrow.isoformat()

    data = fetch_prices(date_str)
    periods = find_negative_periods(data)

    if not periods:
        print(f"Keine negativen Strompreise am {date_str} ({BIDDING_ZONE}).")
        return 0

    message = build_message(date_str, periods)
    print(message)
    send_email(f"Negative Strompreise am {date_str}", message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
