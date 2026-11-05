# Entwicklungsstand

Stand: 2026-11-05. Arbeitsbranch: `develop/sparkyfitness`.

## Ziel und Arbeitsweise

Eine standardmäßig lesende, mit optionalen Schreibaktionen HACS-kompatible Home-Assistant-Integration für
SparkyFitness entwickeln. Zuerst eine funktionsfähige Basis, danach abgegrenzte
Erweiterungen. Jeder funktionsfähige Schritt erhält nach relevanten Prüfungen
einen eigenen Commit. Änderungen regelmäßig in den Entwicklungsbranch übertragen;
`main` bleibt bis zu einer bewussten Übernahme unverändert.

Dieses Dokument bei jedem abgeschlossenen Arbeitsschritt aktualisieren. Keine
Zugangsdaten oder echten Gesundheitsdaten in Code, Tests, Logs oder Commits
aufnehmen. Keine Änderungen am produktiven Home-Assistant-Server durchführen.

## Abgeschlossene Schritte

1. **API-Recherche und Basisintegration** — Commit `b1c5ece`.
   - Asynchroner GET-Client, Identitätsprüfung, getrennte Konten und HTTP-Sitzungen.
   - UI-Konfiguration, Options Flow und erneute Anmeldung bei Schlüsselwechsel.
   - DataUpdateCoordinator, standardmäßig 15 Minuten, konfigurierbare Zeitzone.
   - Ernährungs-/Zielsensoren, Körpermessungen, Training und Schlaf.
   - Dynamische Messkategorien einschließlich vorhandener Garmin-Importwerte.
   - Umgang mit fehlenden Werten, Netzwerkfehlern, HTTP 429 und Tageswechseln.
   - Deutsche/englische Übersetzungen und synthetische automatisierte Tests.
2. **Dokumentation und HACS-Vorbereitung** — Commit `c0dfff8`.
   - README, API-Vertrag, Unraid-Anleitung und Prüfbericht.
   - HACS-Metadaten, eigene Brand-Icons, MIT-Lizenz.
   - GitHub Actions für pytest/Ruff, HACS und Hassfest vorbereitet.
3. **Nachvollziehbarer Entwicklungsablauf** — Commit mit dieser Datei.
   - Entwicklungsbranch, Fortschrittsdokument und dauerhafte Arbeitsanweisungen.
   - Tests vor dem Commit erneut ausgeführt; anschließend Übertragung nach GitHub.

Die ersten beiden Schritte wurden vor Einführung dieses Fortschrittsdokuments
lokal erstellt. Die erste Übertragung enthält diese Historie vollständig.

## Verifikation

Umgebung: Python 3.13.16, Home Assistant 2026.2.3,
pytest-homeassistant-custom-component 0.13.316.

- Aktuell 80 Tests bestanden; Statement-Abdeckung 89 % (538 Statements).
  Historischer 0.1.0-Stand: 42 Tests / 91 %.
- Ruff-Lint und Formatprüfung bestanden.
- Python-Kompilierung, JSON-/Übersetzungsprüfung und `git diff --check` bestanden.
- Ein lokaler aiohttp-Testserver prüft echte HTTP-Anfragen mit synthetischen Daten.
- HA-Tests prüfen unter anderem zwei Konten, Entity-Registrierung, dynamische
  Kategorien, Wiederverbindung, Schlüsselwechsel, Polling und Tageswechsel.
- Bisheriger GitHub-Lauf: Tests und Hassfest erfolgreich. HACS verweigert
  private Repositories; jetzt ausdrücklich bedingter Skip. Abschließender
  Implementierungslauf ec7e866: Tests, Ruff, Bandit, Paketbau und Hassfest erfolgreich.

Die Sandbox ließ die asynchrone HA-Testinitialisierung hängen. Über den unterstützten
Freigabeweg ausgeführte Tests funktionieren. Keine Assertions wurden deaktiviert.
Details: [VALIDATION.md](docs/VALIDATION.md).

## Bekannte Grenzen und offene Prüfungen

- Der Benutzer hat Installation und Lesebetrieb von 0.1.0 erfolgreich bestätigt.
  Schreibaktionen von 0.2.0 sind ausschließlich synthetisch getestet; kein
  produktiver Server wurde durch den Agenten verändert.
- Die API ist anhand SparkyFitness 1.11.0 geprüft; ältere Versionen und weitere
  Home-Assistant-Versionen sind nicht umfassend getestet.
- Fehlende optionale API-Endpunkte erzeugen keine erfundenen Sensorwerte. Wenn
  alle fehlen, kann die Einrichtung ohne Sensoren enden.
- Energie-/Volumensensoren haben bewusst keine Statistikklasse. Weitere
  Statistikfunktionen benötigen eine eigene fachliche Prüfung.
- Schlaf nutzt den längsten Tagesdatensatz, um überlappende Quellen nicht zu
  summieren. Nickerchen und mehrere Schlafquellen werden nicht zusammengeführt.
- Benutzerdefinierte Messkategorien sind dynamisch; benutzerdefinierte Nährstoffe
  sind noch nicht implementiert.
- Ein zukünftiger jüngster Datensatz einer `All`-Kategorie wird ignoriert;
  es wird nicht nach einem älteren Datensatz gesucht.
- Keine Garmin-Synchronisationsauslösung oder historische Rückbefüllung des
  Home-Assistant-Recorders. Sechs Schreibaktionen sind ab 0.2.0 opt-in verfügbar.
- Keine derzeit reproduzierten Fehler in der bestandenen Testsuite; die oben
  genannten Grenzen und ungeprüften Deploymentpfade bleiben ausdrücklich offen.

## Bereitgestellter Deploymentkontext

Der Benutzer betreibt beide Anwendungen als Unraid-Container mit jeweils eigener
IP und zusätzlich eigenen Reverse-Proxy-Adressen. Nach seiner Angabe jeweils
neueste Version; exakte Versionsnummern fehlen noch. Zeitzone vermutlich Berlin,
noch zu bestätigen. Keine API-Schlüssel oder persönlichen Messwerte benötigt.

## Nächste Schritte

1. GitHub-Actions des erweiterten Entwicklungsbranches prüfen; tatsächliche Fehler beheben,
   passende lokale Prüfungen ausführen und separat committen/pushen.
2. Exakte HA-/SparkyFitness-Versionen und Profilzeitzone für den Live-Test klären.
3. Benutzer führt den begrenzten Installationstest gemäß
   [UNRAID.md](docs/UNRAID.md) selbst aus; nur Erfolg/Fehlerklassen und gegebenenfalls
   redigierte Antwortstrukturen rückmelden lassen.
4. Beobachtete Kompatibilitätsprobleme zunächst mit synthetischen Regressionstests
   reproduzieren, anschließend in kleinen Schritten beheben.
5. Erst nach diesen Prüfungen eine Übernahme nach `main` bzw. einen Release
   vorbereiten. Kein automatischer Eingriff in die produktive Installation.

## Fortsetzung ohne erneute Grundrecherche

Checkout: `/workspace/ha-sparkyfitness`. Vor Arbeiten `git status` prüfen und
vorhandene Änderungen erhalten. Keine neuen Worktrees ohne ausdrücklichen Auftrag.

API-Vertrag, Quellpfade, Endpunkte und Datenbedeutung stehen in
[API.md](docs/API.md). Gepinnter untersuchter Upstream-Commit:
`120dc997f79220544fc72591d01c251090dcff1b`; Release `v1.11.0`:
`0d8525e88ea7b116a92cd3aa35f622f7682201e2`. Der ursprüngliche Recherchecheckout
unter `/tmp/sparkyfitness-upstream` ist nur eine optionale lokale Arbeitshilfe.

```sh
uv python install 3.13
uv venv --python 3.13 --managed-python .venv  # nur wenn .venv fehlt
uv pip install --python .venv/bin/python -r requirements-dev.txt
.venv/bin/python -m pytest -q --timeout=30
.venv/bin/ruff check custom_components tests scripts
.venv/bin/ruff format --check custom_components tests scripts
.venv/bin/bandit -r custom_components -q
git diff --check
```

Module: `api.py` = Transport/Authentifizierung; `data.py` = Transformation;
`coordinator.py` = Aktualisierung/Datum; `sensor.py` = Entitäten;
`config_flow.py` = Einrichtung/Optionen/erneute Anmeldung.

## Schritt 4: Schreibaktionen (0.2.0)

Sechs explizite Admin-Aktionen für Körpermessungen, eigene Kategorien, Wasser,
Schlaf, Ernährung und Training implementiert. Standard aus, Aktivierung pro
Konto; Reconfigure-Flow erlaubt Austausch eines noch gültigen Leseschlüssels.
Identität vor jedem Write, feste Endpunkte/Felder, Werte-/Datumsprüfung,
Kategorienprüfung, pro Konto serialisierte Writes, keine automatischen POST-Retries.
69 synthetische Tests bestanden; Ruff-Lint/Formatierung geprüft.
Anleitung: docs/WRITING.md. Nächster Schritt: offizielles Logo/Lizenz,
Sicherheitsbericht und HACS-/Release-Workflow. Der bisherige HACS-Action-Fehler
ist diagnostiziert: Der Validator lehnt private Repositories ab; Tests und
Hassfest des bisherigen GitHub-Laufs waren erfolgreich.

## Schritt 5: Branding, Sicherheit und Distribution

Offizielles Logo unverändert aus dem gepinnten Upstream übernommen; SHA-256
durch Tests abgesichert. Vollständige nichtkommerzielle Upstream-Lizenz und
Attribution im brand-Ordner; ursprünglicher Code weiterhin MIT, Grafik ausgenommen.
SECURITY.md dokumentiert Vertrauensgrenzen, POST-Retry-Risiko, HA-Trace/Recorder-
Datenschutz und beobachtete Upstream-Protokollierung von Messwerten.

Bandit 1.8.6: keine Befunde. Alle 80 Tests, Ruff und Paketprüfung bestanden.
Nach Writes wird eine bestätigte Datensatzantwort verlangt; leere/fehlerhafte
200-Antworten werden nicht als gespeichert gemeldet. CI baut ein reproduzierbares
Installations-ZIP als GitHub-Artefakt; Dependabot für Entwicklungsabhängigkeiten
und Actions vorbereitet. docs/DISTRIBUTION.md beschreibt private Downloads,
spätere öffentliche HACS-Veröffentlichung und Updates. Kein Add-on nötig.
Repository weiterhin privat, main unverändert, kein Release veröffentlicht.
Schreib-Live-Test weiterhin offen; Benutzer muss Schreiboption und passenden
API-Schlüssel selbst setzen.

## Bestätigte Übergabe 0.2.0

Commits: `9d41a33` (Schreibaktionen), `ec7e866` (Logo, Sicherheitsprüfung,
Distribution). Beide nach `origin/develop/sparkyfitness` übertragen.
GitHub-Lauf [42118750136](https://github.com/Lupusred/ha-sparkyfitness/actions/runs/42118750136)
erfolgreich: Tests inkl. Pakettests, Ruff, Bandit, Artifact-Upload und Hassfest.
HACS ausdrücklich übersprungen (privat).
[Installationsartefakt sparkyfitness-0.2.0](https://github.com/Lupusred/ha-sparkyfitness/actions/runs/42118750136/artifacts/13456273662)
verfügbar (30 Tage Aufbewahrung). Keine öffentliche Freigabe oder Produktionsänderung.
Nächster fachlicher Schritt: Benutzer testet gezielt eine Schreibaktion nach
Aktivierung gemäß docs/WRITING.md. GitHub-Status zukünftiger Commits separat prüfen.
