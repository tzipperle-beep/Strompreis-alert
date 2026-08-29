# Strompreis-Alert

Schickt täglich eine E-Mail, falls der Day-Ahead-Strompreis am **nächsten
Tag** zeitweise negativ ist – inkl. Zeitraum (von/bis).

Datenquelle: [energy-charts.info Day-Ahead-Price-API](https://api.energy-charts.info/#/prices/day_ahead_price_price_get)
(Standard-Preiszone: `DE-LU`).

Versand erfolgt per SMTP (Standard: Gmail).

## Einmaliges Setup

1. **App-Passwort erstellen** (bei Gmail)
   - In den Google-Kontoeinstellungen unter "Sicherheit" → "App-Passwörter"
     ein neues App-Passwort erzeugen (erfordert aktivierte
     2-Faktor-Authentifizierung).
   - Das generierte 16-stellige Passwort notieren.

2. **GitHub Repo Secrets/Variablen anlegen** (Settings → Secrets and variables → Actions)
   - Secret `SMTP_USER` = deine Gmail-Adresse, z. B. `tzipperle@gmail.com`
   - Secret `SMTP_PASSWORD` = das App-Passwort aus Schritt 1
   - Secret `EMAIL_TO` = Empfänger-Adresse (kann identisch mit `SMTP_USER` sein)
   - Optional Variable `BIDDING_ZONE` (Standard: `DE-LU`, z. B. `AT`, `CH`)
   - Optional Variable `SMTP_HOST` / `SMTP_PORT`, falls kein Gmail genutzt wird
     (Standard: `smtp.gmail.com` / `465`)

3. Fertig. Der Workflow [`strompreis-alert.yml`](.github/workflows/strompreis-alert.yml)
   läuft automatisch zweimal täglich (13:00 und 19:00 Uhr MESZ, im Winter
   wegen der fixen UTC-Zeit 12:00 und 18:00 Uhr MEZ) und prüft die Preise für
   den nächsten Tag. Gibt es negative Preisperioden, kommt eine E-Mail wie:

   ```
   Betreff: Negative Strompreise am 2026-06-28

   ⚡ Negative Strompreise am 2026-06-28 (DE-LU):
   - 13:00 bis 16:00 Uhr
   - 23:00 bis 00:00 Uhr
   ```

   Gibt es keine negativen Preise, wird **keine** Mail geschickt (nur ein
   Log-Eintrag im Workflow-Run).

## Keepalive

GitHub deaktiviert geplante (`cron`) Workflows automatisch, wenn ein Repository
60 Tage lang keinen neuen Commit erhält ("disabled_inactivity") – der Alert
würde dann stillschweigend aufhören zu laufen, ohne Fehlermeldung.

Der zusätzliche Workflow [`keepalive.yml`](.github/workflows/keepalive.yml)
läuft deshalb einmal im Monat und committet einen Zeitstempel in
`.github/keepalive.txt`. Das hält das Repo "aktiv" und verhindert die
automatische Deaktivierung. Falls der Haupt-Workflow trotzdem einmal
deaktiviert wird (z. B. nach sehr langer Pause): Tab "Actions" → Workflow
auswählen → Button "Enable workflow" klicken.

## Manuell testen

Workflow manuell über den Tab "Actions" → "Negativer Strompreis E-Mail-Alert" →
"Run workflow" anstoßen, oder lokal:

```bash
pip install -r requirements.txt
export SMTP_USER=tzipperle@gmail.com
export SMTP_PASSWORD=xxxx        # App-Passwort
export EMAIL_TO=tzipperle@gmail.com
export BIDDING_ZONE=DE-LU        # optional
python negative_price_alert.py
```
