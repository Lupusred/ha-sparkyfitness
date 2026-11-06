<p align="center">
  <img src="custom_components/sparkyfitness/brand/icon.png" alt="SparkyFitness" width="128">
</p>

# SparkyFitness für Home Assistant

Fitness- und Gesundheitsdaten aus deinem [SparkyFitness-Server](https://github.com/CodeWithCJ/SparkyFitness)
in Home Assistant anzeigen – und ausgewählte Messungen bei Bedarf zurückschreiben.
Eine eigenständige Custom-Integration, installierbar und aktualisierbar über **HACS**.

[![Validierung](https://github.com/Lupusred/ha-sparkyfitness/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/Lupusred/ha-sparkyfitness/actions/workflows/validate.yml)
[![GitHub Release](https://img.shields.io/github/v/release/Lupusred/ha-sparkyfitness)](https://github.com/Lupusred/ha-sparkyfitness/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/docs/faq/custom_repositories/)

**[Installation](docs/INSTALLATION.md) · [Schreibaktionen](docs/WRITING.md) · [Sensoren & API](docs/API.md) · [Dokumentation](docs/README.md) · [Änderungen](CHANGELOG.md)**

## Was die Integration bietet

| Bereich | Funktionen |
|---|---|
| Ernährung | Kalorien, Ziele, verbleibende Kalorien, Makronährstoffe, Ballaststoffe, Zucker, Natrium und Wasser |
| Körper | Gewicht, Körperfett, Muskel-/Knochenmasse, Körperwasser und verfügbare Körpermaße |
| Aktivität & Schlaf | Schritte, Training, Schlafwerte und tatsächlich in SparkyFitness gespeicherte Garmin-Werte |
| Eigene Messungen | Dynamische Sensoren für selbst angelegte Kategorien, einschließlich Zahlen und Text |
| Einrichtung | UI-Konfiguration, getrennte Konten, deutsche/englische Oberfläche, Zeitzone und Aktualisierungsintervall |
| Optionales Schreiben | Körpermessungen, eigene Kategorien, Wasser, Schlaf, Lebensmittel- und Trainingseinträge |

Es werden nur Daten angezeigt, die die Server-API tatsächlich liefert. Fehlende
Werte werden nicht durch erfundene Messungen ersetzt. Die Integration ruft keine
Garmin-Synchronisierung auf; sie liest bereits nach SparkyFitness importierte Daten.

## In HACS installieren

Voraussetzungen: **Home Assistant ab 2026.2**, installiertes HACS und ein aus HA
 erreichbarer SparkyFitness-Server. Die API wurde gegen **SparkyFitness 1.11.0**
geprüft. Ein separates Add-on oder weiterer Docker-Container ist nicht nötig.

[![Repository in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Lupusred&repository=ha-sparkyfitness&category=integration)

Alternativ manuell in HACS hinzufügen:

1. **HACS → Menü ⋮ → Benutzerdefinierte Repositories** öffnen.
2. `https://github.com/Lupusred/ha-sparkyfitness` eintragen, Typ **Integration** wählen.
3. **SparkyFitness for Home Assistant** suchen und herunterladen.
4. Home Assistant neu starten.
5. **Einstellungen → Geräte & Dienste → Integration hinzufügen → SparkyFitness** öffnen.
6. Server-URL und einen eigenen SparkyFitness-API-Schlüssel eingeben.

Das Repository ist ein **HACS Custom Repository**, noch kein Eintrag im
HACS-Standardkatalog. Falls du vorher manuell installiert hast, kannst du die
Integration in HACS herunterladen und danach HA neu starten; die vorhandenen
Integrationseinträge bleiben bestehen. Vor dem Wechsel den Integrationsordner sichern.

**[Ausführliche Installation, Umstieg und Updates →](docs/INSTALLATION.md)**

## Verbindung und Aktualisierung

Verwende die erreichbare SparkyFitness-Webadresse, beispielsweise die LAN-Adresse
mit Webport oder eine HTTPS-Reverse-Proxy-Adresse mit gültigem Zertifikat.
`localhost` im HA-Container bezeichnet diesen Container, nicht SparkyFitness.

Für den Lesebetrieb genügt ein eigener **Read-only-API-Schlüssel** aus
SparkyFitness → Settings → API Key Management. In den Integrationsoptionen die
Zeitzone mit dem SparkyFitness-Profil abgleichen, beispielsweise `Europe/Berlin`.

Die Daten werden beim Laden der Integration, danach standardmäßig alle
**15 Minuten** und zusätzlich beim Tageswechsel aktualisiert. Das Intervall ist
zwischen 5 und 1440 Minuten einstellbar.

## Werte nach SparkyFitness schreiben

Schreiben ist **standardmäßig ausgeschaltet**, auch nach einem Update.
Aktiviere es ausdrücklich in den Optionen des gewünschten Kontos und hinterlege
über **Neu konfigurieren** einen API-Schlüssel mit Schreibrechten.

Danach findest du unter **Entwicklerwerkzeuge → Aktionen** sechs Aktionen:

- `sparkyfitness.set_body_measurements`
- `sparkyfitness.record_custom_measurement`
- `sparkyfitness.record_water`
- `sparkyfitness.record_sleep`
- `sparkyfitness.log_food`
- `sparkyfitness.log_exercise`

Vergangene Tage sind möglich. Berechnete Tagesbilanzen werden nicht direkt
überschrieben. Ein Schreibaufruf wird nach einem Timeout nicht automatisch
wiederholt, damit keine ungewollten Doppeleinträge entstehen.

**[Aktivierung, Einheiten, Beispiele und Wiederholungsverhalten →](docs/WRITING.md)**

## Updates

Neue GitHub-Releases erscheinen in HACS als verfügbare Versionen. Update dort
herunterladen, die [Änderungen](CHANGELOG.md) lesen und Home Assistant neu starten.
Das Konto muss dafür nicht gelöscht oder neu eingerichtet werden. Verwende für
reguläre Installation Releases von `main`; `develop/sparkyfitness` ist der
Entwicklungsbranch.

## Dokumentation und Hilfe

| Thema | Dokument |
|---|---|
| Installation, Umstieg von manueller Installation, Updates | [Installationsanleitung](docs/INSTALLATION.md) |
| Home Assistant als Docker-Container unter Unraid | [Unraid-Anleitung](docs/UNRAID.md) |
| Schreibaktionen und Automationen | [Schreiben nach SparkyFitness](docs/WRITING.md) |
| Sensoren, API-Vertrag und bekannte Grenzen | [API-Dokumentation](docs/API.md) |
| Datenschutz und Sicherheitsgrenzen | [Sicherheitsinformationen](SECURITY.md) |
| Tatsächlich ausgeführte Prüfungen | [Testbericht](docs/VALIDATION.md) |
| Entwicklungsstand und nächste Schritte | [PROGRESS.md](PROGRESS.md) |
| Fehler oder Funktionswunsch | [GitHub Issues](https://github.com/Lupusred/ha-sparkyfitness/issues) |

## Stand und Datenschutz

Version **0.2.0**: 80 automatisierte Tests bestanden; getestet mit Home Assistant
2026.2.3/Python 3.13 und synthetischen API-Daten. Die manuelle Installation und der
Lesebetrieb wurden vom ersten Benutzer bestätigt. **Schreibfunktionen sind noch
nicht live gegen eine produktive Installation geprüft.** Einzelne Felder hängen
von Serverversion, Importquellen und vorhandenen Daten ab.

Die Integration verbindet sich nur mit dem eingestellten Server. Keine Übertragung
von Gesundheitsdaten an Garmin oder andere Drittanbieter durch diese Integration.
TLS-Prüfung bleibt aktiv; lokales HTTP verschlüsselt den Datenverkehr nicht.
HA speichert den API-Schlüssel in seiner Konfiguration; Backups und Zugriff darauf
entsprechend schützen. Recorder und Automation-Traces können Messwerte speichern.
Siehe [SECURITY.md](SECURITY.md), auch zu Protokollen auf dem SparkyFitness-Server.

## Entwicklung

```sh
uv python install 3.13
uv venv --python 3.13 --managed-python .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/python -m pytest -q --timeout=30
.venv/bin/ruff check custom_components tests scripts
.venv/bin/ruff format --check custom_components tests scripts
.venv/bin/bandit -r custom_components -q
```

[AGENTS.md](AGENTS.md) und [PROGRESS.md](PROGRESS.md) beschreiben den Arbeitsablauf.
Tests verwenden ausschließlich synthetische Daten und benötigen keine echten Keys.

## Lizenz und Zuordnung

Unabhängige Community-Integration, keine offizielle Home-Assistant- oder
SparkyFitness-Veröffentlichung. Originaler Integrationscode: [MIT](LICENSE), mit [separaten Grafikbedingungen](NOTICE.md).
Das offizielle SparkyFitness-Logo wurde unverändert übernommen und unterliegt der
[Upstream-Lizenz für nichtkommerzielle Nutzung](custom_components/sparkyfitness/brand/LICENSE.upstream),
nicht der MIT-Lizenz. Kommerzielle Nutzung der Grafik erfordert die entsprechende
Erlaubnis des Rechteinhabers. [Quellenangabe](custom_components/sparkyfitness/brand/NOTICE.md).

Ab 0.3.0 stehen zwölf direkte Eingabe-Entitäten für heutige Körpermessungen bereit.
[Einrichtung und Dashboard-Nutzung](docs/WRITING.md#direkte-eingabe-über-entitäten-ab-030).
