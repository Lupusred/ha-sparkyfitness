# Distribution und Veröffentlichung

[← Dokumentation](README.md)

## Öffentliche Installation

Das Repository wird auf ausdrücklichen Benutzerauftrag öffentlich bereitgestellt.
`main` enthält den veröffentlichten Stand, `develop/sparkyfitness` die weitere
Entwicklung. Anwender installieren das öffentliche Repository über HACS als
Custom Repository; [Installationsanleitung](INSTALLATION.md).

Ein HACS-Standardkatalogeintrag ist nicht Teil dieser Veröffentlichung.
Home Assistant Container benötigt eine Custom-Integration, kein Add-on.

## Pakete

`python scripts/package.py` erstellt `dist/sparkyfitness.zip` mit dem vollständigen
Ordner `sparkyfitness/`, ohne Tests, Caches oder Zugangsdaten. Das Paket enthält die
Logo-Lizenz und Attribution. GitHub Actions erstellt es nach den lokalen Checks
auch als Download-Artefakt mit 30 Tagen Aufbewahrung.

Der Workflow `release.yml` erstellt nach Veröffentlichung eines Release dessen
Installations-ZIP und hängt es dauerhaft an. Er prüft, dass Release-Tag und
Manifestversion übereinstimmen. Der Upload verwendet ausschließlich GitHubs
kurzlebiges Workflow-Token; eigene Zugangsdaten sind nicht erforderlich.
Ein vorhandener Anhang wird nicht stillschweigend überschrieben. HACS verwendet die Repositorystruktur
`custom_components/sparkyfitness/` am Release-Tag. Deshalb ist `zip_release` in
`hacs.json` nicht aktiviert; das manuelle ZIP hat einen umschließenden Ordner.

## Ablauf für künftige Releases

1. Änderungen auf `develop/sparkyfitness` entwickeln, relevante Tests ausführen
   und `PROGRESS.md` aktualisieren. Keine echten Gesundheitsdaten in Fixtures.
2. Manifestversion und CHANGELOG aktualisieren; Benutzerkompatibilität und noch
   offene Live-Prüfungen klar dokumentieren.
3. GitHub-Validierung einschließlich Tests, Ruff, Bandit, Hassfest und HACS abwarten.
4. Den geprüften Stand nach bewusstem Veröffentlichungsauftrag nach `main`
   übernehmen. Keine Force-Pushes.
5. Einen eindeutigen Tag `vX.Y.Z` passend zur Manifestversion anlegen und einen
   GitHub-Release mit aussagekräftigen Release Notes veröffentlichen.
6. Das aus genau diesem Tag erzeugte Installations-ZIP an den Release anhängen.
7. Öffentliche Repository-/Release-Metadaten, erfolgreichen HACS-Check und den
   Download prüfen. Keine Veröffentlichung als bestanden darstellen, solange
   ein erforderlicher Check fehlt.

Keine automatischen Änderungen an produktiven Home-Assistant-Installationen.
Die ersten öffentlichen Schreibfunktionen sind synthetisch getestet; gezielte
Live-Rückmeldungen bleiben eine separate Prüfung.

## Lizenz

Originaler Integrationscode: MIT. Offizielles SparkyFitness-Logo:
nichtkommerzielle Upstream-Bedingungen in `brand/LICENSE.upstream`, nicht MIT.
Lizenz und NOTICE müssen in allen Installationspaketen verbleiben. Das Projekt
ist eine unabhängige Community-Integration und keine offizielle Upstream-Ausgabe.
