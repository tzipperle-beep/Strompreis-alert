#!/usr/bin/env python3
"""Sendet eine Telegram-Nachricht, wenn der Day-Ahead-Strompreis am naechsten Tag negativ ist."""

import os
import sys
from datetime import datetime, timedelta, timezone

import requests

ENERGY_CHARTS_URL = "https://api.energy-charts.info/price"
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"

BIDDING_ZONE = os.environ.get("BIDDING_ZONE", "DE-LU")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

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


def send_telegram_message(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN und TELEGRAM_CHAT_ID muessen gesetzt sein."
        )
    url = TELEGRAM_API_URL.format(token=TELEGRAM_BOT_TOKEN)
    response = requests.post(
        url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=30
    )
    response.raise_for_status()


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
    send_telegram_message(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
