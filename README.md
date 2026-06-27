# Strompreis-Alert

Schickt täglich eine Telegram-Nachricht, falls der Day-Ahead-Strompreis am
**nächsten Tag** zeitweise negativ ist – inkl. Zeitraum (von/bis).

Datenquelle: [energy-charts.info Day-Ahead-Price-API](https://api.energy-charts.info/#/prices/day_ahead_price_price_get)
(Standard-Preiszone: `DE-LU`).

## Einmaliges Setup

1. **Telegram-Bot erstellen**
   - Mit [@BotFather](https://t.me/BotFather) chatten, `/newbot` ausführen,
     den angezeigten **Bot-Token** notieren.
   - Dem eigenen Bot eine Nachricht schreiben (z. B. `/start`), damit er dich
     kennt.
   - Eigene **Chat-ID** ermitteln, z. B. über:
     `https://api.telegram.org/bot<TOKEN>/getUpdates`
     (im JSON unter `message.chat.id`).

2. **GitHub Repo Secrets/Variablen anlegen** (Settings → Secrets and variables → Actions)
   - Secret `TELEGRAM_BOT_TOKEN` = dein Bot-Token
   - Secret `TELEGRAM_CHAT_ID` = deine Chat-ID
   - Optional Variable `BIDDING_ZONE` (Standard: `DE-LU`, z. B. `AT`, `CH`)

3. Fertig. Der Workflow [`negative-price-alert.yml`](.github/workflows/negative-price-alert.yml)
   läuft automatisch täglich um 13:00 UTC (nachdem die Day-Ahead-Auktion
   veröffentlicht ist) und prüft die Preise für den nächsten Tag. Gibt es
   negative Preisperioden, kommt eine Telegram-Nachricht wie:

   ```
   ⚡ Negative Strompreise am 2026-06-28 (DE-LU):
   - 13:00 bis 16:00 Uhr
   - 23:00 bis 00:00 Uhr
   ```

   Gibt es keine negativen Preise, wird **keine** Nachricht geschickt (nur ein
   Log-Eintrag im Workflow-Run).

## Manuell testen

Workflow manuell über den Tab "Actions" → "Negative Strompreis Alert" →
"Run workflow" anstoßen, oder lokal:

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=xxxx
export TELEGRAM_CHAT_ID=xxxx
export BIDDING_ZONE=DE-LU   # optional
python negative_price_alert.py
```
