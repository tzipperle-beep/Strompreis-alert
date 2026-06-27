# Strompreis-Alert

Schickt täglich eine WhatsApp-Nachricht, falls der Day-Ahead-Strompreis am
**nächsten Tag** zeitweise negativ ist – inkl. Zeitraum (von/bis).

Datenquelle: [energy-charts.info Day-Ahead-Price-API](https://api.energy-charts.info/#/prices/day_ahead_price_price_get)
(Standard-Preiszone: `DE-LU`).

Versand erfolgt über [CallMeBot](https://www.callmebot.com/blog/free-api-whatsapp-messages/),
einen kostenlosen Drittanbieter-Dienst für WhatsApp-Nachrichten an die eigene
Nummer.

## Einmaliges Setup

1. **CallMeBot aktivieren**
   - Die Nummer `+34 644 51 73 49` zu deinen WhatsApp-Kontakten hinzufügen.
   - Dieser Nummer per WhatsApp die Nachricht `I allow callmebot to send me messages`
     schicken.
   - Du bekommst per WhatsApp deinen persönlichen **API-Key** zurück
     (z. B. `123456`).

2. **GitHub Repo Secrets/Variablen anlegen** (Settings → Secrets and variables → Actions)
   - Secret `WHATSAPP_PHONE` = deine Telefonnummer im internationalen Format
     mit `+`, z. B. `+491701234567`
   - Secret `CALLMEBOT_API_KEY` = dein CallMeBot-API-Key
   - Optional Variable `BIDDING_ZONE` (Standard: `DE-LU`, z. B. `AT`, `CH`)

3. Fertig. Der Workflow [`negative-price-alert.yml`](.github/workflows/negative-price-alert.yml)
   läuft automatisch täglich um 13:00 UTC (nachdem die Day-Ahead-Auktion
   veröffentlicht ist) und prüft die Preise für den nächsten Tag. Gibt es
   negative Preisperioden, kommt eine WhatsApp-Nachricht wie:

   ```
   ⚡ Negative Strompreise am 2026-06-28 (DE-LU):
   - 13:00 bis 16:00 Uhr
   - 23:00 bis 00:00 Uhr
   ```

   Gibt es keine negativen Preise, wird **keine** Nachricht geschickt (nur ein
   Log-Eintrag im Workflow-Run).

## Manuell testen

Workflow manuell über den Tab "Actions" → "Negativer Strompreis WhatsApp-Alert" →
"Run workflow" anstoßen, oder lokal:

```bash
pip install -r requirements.txt
export WHATSAPP_PHONE=+491701234567
export CALLMEBOT_API_KEY=xxxx
export BIDDING_ZONE=DE-LU   # optional
python negative_price_alert.py
```

## Hinweis zu CallMeBot

CallMeBot ist ein inoffizieller, kostenloser Dienst für persönliche
Benachrichtigungen (kein offizielles WhatsApp-Business-API). Für gelegentliche
Alerts wie diesen ist er ausreichend zuverlässig, für unternehmenskritische
oder massenhafte Nachrichten ist er nicht gedacht.
