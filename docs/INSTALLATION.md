# Installation und Updates

[← Dokumentation](README.md)

## Voraussetzungen

- Home Assistant ab 2026.2; getestet mit Core 2026.2.3.
- SparkyFitness-API 1.11.0 als geprüfte Basis. Abweichende Versionen können weniger
  oder andere Felder liefern.
- Erreichbarkeit des SparkyFitness-Webservers aus Home Assistant.
- Für HACS: [HACS bereits installiert](https://hacs.xyz/docs/use/download/download/).

Die Integration läuft direkt in Home Assistant, auch in Home Assistant Container
unter Unraid. Ein Supervisor/Add-on wird dafür nicht benötigt.

## HACS

[Repository in HACS öffnen](https://my.home-assistant.io/redirect/hacs_repository/?owner=Lupusred&repository=ha-sparkyfitness&category=integration)

Oder in HACS unter ⋮ → **Benutzerdefinierte Repositories** hinzufügen:

```text
https://github.com/Lupusred/ha-sparkyfitness
```

Typ **Integration** auswählen, hinzufügen, danach **SparkyFitness for Home Assistant**
herunterladen. Home Assistant neu starten. Es handelt sich um ein Custom Repository;
eine Suche im Standardkatalog allein findet es noch nicht.

## Bereits manuell installiert?

1. Vorhandenen Ordner `/config/custom_components/sparkyfitness` sichern.
2. Repository wie oben zu HACS hinzufügen und dieselbe Integration herunterladen.
3. Home Assistant neu starten.
4. Den vorhandenen SparkyFitness-Eintrag und die Entitäten prüfen. Nicht löschen
   und neu anlegen: die Domain und Unique IDs bleiben beim Update erhalten.
5. Künftige Updates in HACS installieren.

Das gilt auch für den bisherigen Entwicklungsstand 0.1.0/0.2.0. Die Schreiboption
bleibt nach dem Update ausgeschaltet, wenn du sie nicht selbst aktiviert hast.

## Manuelle Alternative

Unter [Releases](https://github.com/Lupusred/ha-sparkyfitness/releases) das
Installationspaket `sparkyfitness.zip` herunterladen. Es enthält den Ordner
`sparkyfitness/`. Diesen vollständig nach `/config/custom_components/` entpacken;
danach liegt `manifest.json` unter `/config/custom_components/sparkyfitness/`.
Andere Integrationen unverändert lassen, danach HA neu starten.

Bei GitHubs „Source code“-ZIP stattdessen ausschließlich den darin enthaltenen
Ordner `custom_components/sparkyfitness` kopieren.
[Ausführliche Unraid-Anleitung](UNRAID.md).

## Einrichtung

1. SparkyFitness → Settings → API Key Management: einen eigenen Schlüssel
   erzeugen, für die Anzeige genügt **Read-only**.
2. HA → Einstellungen → Geräte & Dienste → Integration hinzufügen → SparkyFitness.
3. Die erreichbare SparkyFitness-Web-URL und den Schlüssel eingeben. Bei Reverse
   Proxy die endgültige URL mit gültigem Zertifikat und ohne vorgeschaltete
   zusätzliche Login-Seite verwenden. Weiterleitungen werden nicht verfolgt.
4. In den Optionen Intervall und Zeitzone einstellen. Standard: 15 Minuten und
   HA-Zeitzone; die Zone muss zum SparkyFitness-Profil passen.
5. Entitäten unter dem angelegten Gerät prüfen. Neue Kategorien werden automatisch
   bei einer späteren Aktualisierung erkannt.

Pro unabhängiges Konto einen eigenen Integrationseintrag anlegen. Keys niemals in
GitHub Issues oder Screenshots weitergeben. Für optionale Schreibfunktionen siehe
[WRITING.md](WRITING.md).

## Updates und Rückkehr

HACS prüft GitHub-Releases. Neue Version herunterladen, Release Notes lesen und
HA neu starten. Bei Bedarf in HACS über „Erneut herunterladen“ eine frühere
veröffentlichte Version wählen oder den gesicherten Integrationsordner manuell
wiederherstellen. Für das erste öffentliche Release gibt es noch keine ältere
öffentliche Release-Version.

Bei manuellen Updates immer den kompletten Integrationsordner ersetzen, damit
Aktionsbeschreibungen, Übersetzungen und Logo-Dateien zur Python-Version passen.
Ein Zurücksetzen des Containers oder der Datenbank ist nicht notwendig.

## Häufige Fragen

- **Nicht auffindbar:** Custom Repository in HACS hinzufügen; nach dem Download HA
  neu starten. Bei manueller Installation die Ordnerstruktur kontrollieren.
- **Verbindung fehlgeschlagen:** Erreichbarkeit aus dem HA-Container, Webport,
  endgültige URL, Zertifikat und API-Key prüfen. Nicht die Garmin-Zugangsdaten nutzen.
- **Sensor unbekannt:** Das Feld ist leer oder ungültig. Fehlende Daten werden nicht
  geschätzt. Garmin muss zuvor nach SparkyFitness synchronisiert haben.
- **Nicht verfügbar:** Aktualisierung fehlgeschlagen oder API-Feld verschwunden.
  Beim Tageswechsel können Tageswerte bis zur erfolgreichen Aktualisierung fehlen.
- **Schreiben abgelehnt:** Schreiboption pro Konto aktivieren, richtigen Account
  wählen und einen passenden API-Key über „Neu konfigurieren“ hinterlegen.
- **Logo noch alt:** Nach dem Update Browser-/Frontend-Cache aktualisieren. Die
  Anzeige lokaler Brand-Dateien hängt zusätzlich von der HA-/HACS-Version ab.
