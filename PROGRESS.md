# Entwicklungsstand

Stand: 2026-11-06. Arbeitsbranch: `develop/sparkyfitness`.

Aktueller Stand: **v0.2.0 öffentlich veröffentlicht**, PR #1 übernommen,
HACS als benutzerdefiniertes Repository nutzbar. Release-Commit:
`3f0a1a021d7c64f39295b05800c133eff060ca67`.
[Release und Installationspaket](https://github.com/Lupusred/ha-sparkyfitness/releases/tag/v0.2.0).
Tests, Hassfest und öffentlicher HACS-Check erfolgreich; öffentlicher ZIP-Download
gegen den lokalen Paketbau geprüft. Ältere Abschnitte sind Entwicklungshistorie.
Keine Änderungen am produktiven Home-Assistant-Server.

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
- Öffentlicher GitHub-Lauf 42178478537 (Versuch 2): Tests, Ruff, Bandit,
  Paketbau, Hassfest und HACS erfolgreich. Frühere private Läufe sind unten
  ausschließlich als Entwicklungshistorie dokumentiert.

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

1. Benutzer übernimmt die veröffentlichte Integration gemäß
   [INSTALLATION.md](docs/INSTALLATION.md) in HACS; vorhandenen HA-Eintrag erhalten.
2. Exakte HA-/SparkyFitness-Versionen und Profilzeitzone beim Live-Test festhalten.
3. Benutzer testet gezielt eine optionale Schreibaktion gemäß
   [WRITING.md](docs/WRITING.md); nur Erfolg/Fehlerklasse ohne persönliche Messwerte
   oder Zugangsdaten rückmelden.
4. Beobachtete Kompatibilitätsprobleme zunächst mit synthetischen Regressionstests
   reproduzieren, anschließend in kleinen Schritten beheben.
5. Weiterentwicklung auf develop/sparkyfitness; spätere Releases bewusst freigeben.
   Kein automatischer Eingriff in die produktive Installation.

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

## Schritt 6: öffentliche HACS-Veröffentlichung vorbereiten

Benutzerauftrag: Repository öffentlich stellen und direkt über GitHub/HACS
nutzbar machen. README als deutschsprachige Projektseite mit offiziellem Logo,
HACS-Einstieg und klarer Navigation neu erstellt; docs/README.md, INSTALLATION.md
und CHANGELOG.md ergänzt. Distribution und Unraid-Anleitung für öffentlichen
Release und Umstieg von manueller Installation aktualisiert.
Vor Freigabe: komplette Git-Historie auf Secrets prüfen, lokale Suite ausführen.
Danach: Sichtbarkeit ändern, geprüften Stand nach main übernehmen, öffentlichen
HACS-Validator prüfen und v0.2.0 mit Installations-ZIP veröffentlichen.
Keine Änderungen an der produktiven HA-Installation.

Vorveröffentlichungsprüfung: Gitleaks 8.24.3 (offizielles Archiv mit SHA-256
verifiziert) hat sämtliche sieben bisherigen lokalen Commits geprüft: keine
Secrets gefunden. 80 Tests, Ruff, Formatierung und Bandit bestanden; 39 lokale
Dokumentationslinks überprüft.

## Historischer Veröffentlichungsstatus: damalige externe Blockaden

Die öffentliche Dokumentation ist in Commit b8103af auf develop/sparkyfitness.
[PR #1](https://github.com/Lupusred/ha-sparkyfitness/pull/1) übernimmt den
geprüften Stand nach main. Ein lokaler Fast-forward wurde vorbereitet, der
Remote-Push nach main jedoch von der automatischen Freigabe abgelehnt: Sie
verlangt eine ausdrückliche Zustimmung genau zur Standardbranch-Übernahme.
Nicht über API-Merge, Defaultbranch-Wechsel oder andere Wege umgehen.

Der ausdrücklich autorisierte Versuch, das Repository öffentlich zu stellen,
wurde von GitHub mit HTTP 403 „Resource not accessible by integration“ abgelehnt.
Metadaten zeigen Administratorrechte des Benutzers, der verbundene App-Zugang
hat jedoch nicht die erforderliche Administrationsberechtigung für Sichtbarkeit.
Kein fehlender API-Key der Anwendung; keine Secrets anfordern. Benutzer muss
GitHub Settings → General → Danger Zone → Change repository visibility → Public
selbst ausführen. Repository bleibt derzeit privat, main remote unverändert.

Release-Entwurf v0.2.0, ID 435813141, ist auf GitHub angelegt und noch nicht
veröffentlicht. Er referenziert den geprüften Entwicklungsstand. Nach Benutzer-
freigabe und erfolgreicher main-Übernahme das endgültige target_commitish prüfen,
öffentlichen HACS-Check ausführen und dann diesen Entwurf veröffentlichen; keinen
zweiten Release anlegen. Falls derselbe Tag inzwischen existiert, zuerst prüfen.

Fortsetzung: (1) öffentliche Sichtbarkeit erneut lesen, (2) ausdrückliche Freigabe
für main berücksichtigen, (3) aktuellen Remote-Stand abgleichen, (4) PR übernehmen,
(5) HACS/Hassfest/Tests auf main bestätigen, (6) vorbereiteten Release veröffentlichen,
(7) öffentliche Downloads prüfen. Produktive HA-Installation unverändert lassen.

Der direkte Upload des Installations-ZIP an den Release-Entwurf wurde mit HTTP
400 abgelehnt; der Entwurf hat daher noch keinen Paketanhang. Kein identischer
Upload erneut versucht. Als reproduzierbarer Distributionsweg ist release.yml
vorbereitet: Nach Veröffentlichung eines Release erzeugt GitHub Actions das ZIP
aus dessen Tag, prüft die Manifestversion und hängt es mit dem kurzlebigen
GitHub-Token an. Dieser Workflow benötigt die freigegebene Übernahme nach main
und ist noch nicht ausgeführt. Aktuelle ZIPs sind weiterhin über Validate-Artefakte
verfügbar. Der Release-Entwurf muss vor Veröffentlichung auf den finalen Commit
einschließlich dieses Workflows gesetzt werden.

## Fortsetzung am 2026-11-06 nach Nutzungslimit

GitHub erneut geprüft: Repository ist jetzt öffentlich; PR #1 weiterhin offen
und mergefähig, Release 435813141 weiterhin Entwurf. Die Sichtbarkeitsblockade
ist damit erledigt. Die zuvor abgelehnte Übernahme nach main bleibt bis zur
ausdrücklichen Freigabe genau dieses Schritts ausgesetzt.

Release-Workflow fertiggestellt und mit Actionlint 1.7.7 (offizieller Download,
SHA-256 verifiziert) ohne Befund geprüft. Der isolierte Pakettest hatte eine
Importreihenfolge-Abhängigkeit zur gesamten Suite; Schemaimport auf Modulebene
verschoben. Danach drei Pakettests separat und alle 80 Tests erfolgreich.
Der Workflow erstellt nach Release-Veröffentlichung das ZIP aus dem Release-Tag
und lädt es mit GitHubs kurzlebigem Token hoch. Kein produktiver Server geändert.

Nächster Schritt: öffentlichen HACS-Check des gepushten Standes bestätigen,
ausdrückliche Freigabe der PR-Übernahme nach main erhalten, Release-Entwurf auf
den endgültigen geprüften Commit setzen und veröffentlichen.

## Freigabe und HACS-Korrektur am 2026-11-06

Der Benutzer hat PR #1 nach main und Veröffentlichung v0.2.0 ausdrücklich
freigegeben. PR #1 wurde übernommen, main steht auf Mergecommit 862260c.
Tests und Hassfest auf main erfolgreich; öffentlicher HACS-Check meldet
NOASSERTION-Lizenzerkennung und fehlende Topics. Der App-Zugang darf Topics
nicht setzen (HTTP 403), Benutzer wurde gebeten, home-assistant und hacs über
About einzutragen.

Für maschinenlesbare MIT-Erkennung wurde der Hinweis auf die ausgenommenen
Logo-Dateien aus LICENSE in die separate NOTICE.md verschoben. Die vollständige
nichtkommerzielle Grafiklizenz in brand/LICENSE.upstream bleibt unverändert
erhalten; keinerlei zusätzliche Grafikrechte erteilt. Dieser Metadatenfix wird
als notwendige Korrektur für den freigegebenen HACS-Release nach main übernommen.
Der bestehende Release-Entwurf bleibt bis zum erfolgreichen öffentlichen Check
unveröffentlicht und muss auf den abschließenden Commit aktualisiert werden.

## Erfolgreiche öffentliche Validierung und Paketabschluss

Topics vom Benutzer gesetzt; GitHub erkennt LICENSE als MIT.
[Validate 42178478537, Versuch 2](https://github.com/Lupusred/ha-sparkyfitness/actions/runs/42178478537)
ist für 68310ef vollständig erfolgreich: Tests, Hassfest und erstmals öffentlicher
HACS-Check. Release-Entwurf auf Tag v0.2.0 korrigiert; Release Notes mit echten
Zeilenumbrüchen formatiert.

Die abschließende Paketkontrolle zeigte: Die Grafiklizenz war enthalten, die
MIT-Code-Lizenz lag bisher nur im Repository-Stamm. LICENSE.md und ein kurzer
Geltungsbereichshinweis liegen jetzt zusätzlich im Integrationsordner, sodass
HACS-Downloads und manuelles ZIP beide Lizenztexte enthalten. Pakettest prüft
exakte Übereinstimmung mit der Root-Lizenz und Anwesenheit sämtlicher Hinweise.
Vor Veröffentlichung den finalen Commit prüfen und Release-Entwurf darauf setzen.

Prüfung dieses Paketabschlusses: drei Pakettests, Ruff-Lint/-Format und
`git diff --check` bestanden; Integrationslogik unverändert.

## Veröffentlichung v0.2.0 abgeschlossen — 2026-11-06

- Freigabe des Benutzers für PR #1 nach main und Release v0.2.0 umgesetzt.
- Release-Tag v0.2.0 verweist auf 3f0a1a021d7c64f39295b05800c133eff060ca67.
- [Validate 42179011923](https://github.com/Lupusred/ha-sparkyfitness/actions/runs/42179011923):
  Tests, Ruff, Formatierung, Bandit, Paketbau, Hassfest und HACS erfolgreich.
- [Release package 42179203911](https://github.com/Lupusred/ha-sparkyfitness/actions/runs/42179203911):
  automatischer ZIP-Bau und Upload erfolgreich.
- Release ID 435813141 öffentlich, kein Entwurf/Prerelease; als neuester Release
  von GitHub bestätigt. Anhang sparkyfitness.zip: 214426 Bytes, 19 Dateien.
- Öffentlicher Download bytegleich zum lokalen reproduzierbaren Paket;
  ZIP-Integrität, Manifestversion und Tag-Commit geprüft.
- SHA-256: `84789ff4d1cf7491eec2f1890d16734abb86a1761b77913dca8d0d8f3f20f66a`.
- Metadatenblockaden erledigt: Repository öffentlich, Topics vom Benutzer gesetzt,
  MIT erkannt. Keine Zugangsdaten veröffentlicht oder Produktionsdienste verändert.

Dieser abschließende Dokumentationscommit folgt auf den unveränderten Release-Tag.
Offen bleiben der HACS-Installationstest beim Benutzer und ein bewusst gewählter
Live-Test der optionalen Schreibaktionen. Die manuelle Installation und der
Lesebetrieb der vorherigen Basis wurden bereits bestätigt. Keine offenen
Veröffentlichungsblockaden; kein Eintrag im HACS-Standardkatalog beantragt.
