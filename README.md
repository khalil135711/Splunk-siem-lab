# Splunk SIEM-Lab

Ein lokales **SIEM-Labor mit Splunk** in Docker. Das Projekt zeigt den Weg von der Log-Quelle bis zum Alarm:
Logs einlesen, Felder extrahieren, Dashboards bauen und Angriffe (SSH-Brute-Force) per Alert erkennen.
Die Logs werden synthetisch erzeugt, es werden keine echten Systeme oder Daten verwendet.

## Inhalt

| Pfad | Zweck |
|---|---|
| `docker-compose.yml` | Startet Splunk Enterprise (Testlizenz) und bindet die App und die Logs ein |
| `scripts/generate_logs.py` | Erzeugt sshd-ähnliche Logs mit Normalbetrieb und Brute-Force-Angriffen |
| `splunk/apps/siem_lab/default/inputs.conf` | Überwacht `auth.log` und schreibt in den Index `lab_auth` |
| `splunk/apps/siem_lab/default/props.conf` | Zeitstempel, Feldextraktion (`user`, `src_ip`, `src_port`, `host`) und Feld `action` |
| `splunk/apps/siem_lab/default/savedsearches.conf` | Zwei geplante Alerts |
| `splunk/apps/siem_lab/default/data/ui/views/auth_overview.xml` | Dashboard „SSH Authentifizierung - Übersicht“ |
| `queries.spl` | Sammlung nützlicher SPL-Abfragen |

## Schnellstart

```bash
cp .env.example .env              # Passwort in .env anpassen
python3 scripts/generate_logs.py --out logs/auth.log --days 1
docker compose up -d
```

Splunk braucht beim ersten Start einige Minuten. Danach ist die Oberfläche unter http://localhost:8000 erreichbar
(Benutzer `admin`, Passwort aus `.env`). In der App **SIEM Lab** findest du das Dashboard und unter
*Einstellungen → Suchen, Berichte und Alarme* die Alerts.

Neue Daten erzeugen (z. B. um die Alerts auszulösen):

```bash
python3 scripts/generate_logs.py --out logs/auth.log --days 2 --seed 7
```

Beenden und aufräumen: `docker compose down -v`

## Erkennungsregeln

| Alert | Logik | Bezug zu ISO 27001:2022 |
|---|---|---|
| SSH Brute Force | ≥ 5 fehlgeschlagene Anmeldungen derselben IP in 5 Minuten | A.8.16 Überwachungstätigkeiten |
| Erfolg nach Fehlversuchen | IP mit ≥ 3 Fehlversuchen und mindestens einem Erfolg, mögliche Kompromittierung | A.8.16, A.5.25 Beurteilung von Ereignissen der Informationssicherheit |

Beispiel-SPL für die Brute-Force-Erkennung:

```spl
index=lab_auth sourcetype=lab:auth action=failure
| stats count AS failures dc(user) AS users BY src_ip
| where failures >= 5
```

## Mögliche Erweiterungen

- Echte Logs per Universal Forwarder einbinden (Linux `auth.log`, Windows Security Events)
- Alert-Aktionen: E-Mail oder Webhook
- Korrelation mit Threat-Intelligence-Listen (Lookups)
- Mapping der Regeln auf MITRE ATT&CK (z. B. T1110 Brute Force)

## Hinweise

- Das Image `splunk/splunk` nutzt die Splunk-Testlizenz. Mit der Free-Lizenz entfallen Alerts, Authentifizierung und einige Funktionen.
- Die Lizenzbedingungen von Splunk (`--accept-license`) gelten für die Nutzung des Images.
- Das Passwort in `.env.example` ist nur ein Platzhalter. Die Datei `.env` gehört nicht ins Repository.

## Lizenz

MIT
