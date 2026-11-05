# Entwicklungsstand

Stand: 2026-11-05. Arbeitsbranch: `develop/sparkyfitness`.

## Ziel und Arbeitsweise

Eine ausschließlich lesende, HACS-kompatible Home-Assistant-Integration für
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

- 42 Tests bestanden; zuletzt gemessene Statement-Abdeckung: 91 %.
- Ruff-Lint und Formatprüfung bestanden.
- Python-Kompilierung, JSON-/Übersetzungsprüfung und `git diff --check` bestanden.
- Ein lokaler aiohttp-Testserver prüft echte HTTP-Anfragen mit synthetischen Daten.
- HA-Tests prüfen unter anderem zwei Konten, Entity-Registrierung, dynamische
  Kategorien, Wiederverbindung, Schlüsselwechsel, Polling und Tageswechsel.
- HACS-/Hassfest-Actions sind vorbereitet; ein erfolgreicher Lauf auf GitHub ist
  bislang nicht verifiziert. Das ist vom lokalen Teststatus zu unterscheiden.

Die Sandbox ließ die asynchrone HA-Testinitialisierung hängen. Über den unterstützten
Freigabeweg ausgeführte Tests funktionieren. Keine Assertions wurden deaktiviert.
Details: [VALIDATION.md](docs/VALIDATION.md).

## Bekannte Grenzen und offene Prüfungen

- Noch kein Live-Test gegen die Installation des Benutzers; kein produktiver
  Server wurde verändert. Version 0.1.0 ist ein erster getesteter Release-Kandidat.
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
- Keine Schreibfunktionen, Garmin-Synchronisationsauslösung oder historische
  Rückbefüllung des Home-Assistant-Recorders.
- Keine derzeit reproduzierten Fehler in der bestandenen Testsuite; die oben
  genannten Grenzen und ungeprüften Deploymentpfade bleiben ausdrücklich offen.

## Bereitgestellter Deploymentkontext

Der Benutzer betreibt beide Anwendungen als Unraid-Container mit jeweils eigener
IP und zusätzlich eigenen Reverse-Proxy-Adressen. Nach seiner Angabe jeweils
neueste Version; exakte Versionsnummern fehlen noch. Zeitzone vermutlich Berlin,
noch zu bestätigen. Keine API-Schlüssel oder persönlichen Messwerte benötigt.

## Nächste Schritte

1. GitHub-Actions des Entwicklungsbranches prüfen; tatsächliche Fehler beheben,
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
.venv/bin/ruff check custom_components tests
.venv/bin/ruff format --check custom_components tests
git diff --check
```

Module: `api.py` = Transport/Authentifizierung; `data.py` = Transformation;
`coordinator.py` = Aktualisierung/Datum; `sensor.py` = Entitäten;
`config_flow.py` = Einrichtung/Optionen/erneute Anmeldung.
