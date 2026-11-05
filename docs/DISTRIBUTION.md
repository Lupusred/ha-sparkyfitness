# GitHub-Installation und Updates

## Integration statt Add-on

SparkyFitness for Home Assistant ist eine Custom-Integration innerhalb von HA.
Ein Home-Assistant-Add-on wäre ein separater Dienst/Container und benötigt
Supervisor (HA OS/Supervised). Der vorhandene HA-Container unter Unraid benötigt
für diese Anbindung eine Integration, keinen zusätzlichen Dienst.

## Aktuell: privater Entwicklungsbranch

`develop/sparkyfitness` enthält die vollständige Umsetzung; `main` wird nicht
ungefragt überschrieben. Der Repositoryzugriff ist privat geblieben. Der offizielle
HACS-Validator lehnt private Repositories ab; deshalb wird dieser CI-Job privat
explizit übersprungen, nicht als erfolgreich validiert dargestellt. pytest,
Ruff, Bandit und Hassfest laufen weiterhin.

GitHub → Actions → erfolgreicher Validate-Lauf des Entwicklungsbranches →
Artifacts → `sparkyfitness-0.2.0` herunterladen. Das GitHub-Artifact-ZIP enthält
`sparkyfitness.zip`. Dieses Installations-ZIP enthält direkt `sparkyfitness/` mit
allen Integrationsdateien, Übersetzungen, Aktionsbeschreibungen und Logo/Lizenz.
GitHub-Artefakte benötigen Repositoryzugriff und werden 30 Tage aufbewahrt.
Alternativ Code → Download ZIP im Entwicklungsbranch verwenden.

Bei einem manuellen Update den bisherigen Integrationsordner sichern, durch den
neuen vollständigen Ordner ersetzen und HA neu starten. Die bestehenden
Integrationseinträge behalten ihre IDs. 0.2.0 schaltet Schreibzugriff nicht
selbstständig ein. Aktivierung und Schlüsselwechsel: [WRITING.md](WRITING.md).

## Späterer Standardweg über HACS

Vor einer öffentlichen Veröffentlichung:

1. Sicherheits-/Lizenzhinweise lesen. Das offizielle Logo hat nichtkommerzielle
   Bedingungen; keine pauschale MIT-Freigabe für die Grafiken behaupten.
2. Die getesteten Entwicklungscommits bewusst über PR nach `main` übernehmen.
   Live-Schreibtests und konkrete Versionskompatibilität dokumentieren.
3. Repository bewusst öffentlich zugänglich machen oder ein dafür freigegebenes
   öffentliches Distributionsrepository verwenden. Sichtbarkeit wurde durch den
   Agenten nicht geändert. Auch die Historie auf persönliche Inhalte prüfen.
4. Validate einschließlich des dann aktiven offiziellen HACS-Jobs erfolgreich
   ausführen. Hassfest und HACS-Erfolg nicht aus dem lokalen Teststatus ableiten.
5. GitHub-Release mit einem Versions-Tag erstellen, der `manifest.json` entspricht
   (aktuell `v0.2.0`). Das ist noch nicht automatisch veröffentlicht worden.
6. In HACS → Benutzerdefinierte Repositories die GitHub-Repository-URL als
   **Integration** hinzufügen, herunterladen und HA neu starten.

HACS lädt die Struktur `custom_components/sparkyfitness/` aus dem Repository bzw.
dem gewählten Release. `hacs.json` verwendet bewusst kein `zip_release`, weil das
manuelle ZIP einen umschließenden `sparkyfitness/`-Ordner enthält. Neue Versionen
mit erhöhter Manifestversion und GitHub-Release erscheinen anschließend in HACS.
Eine Aufnahme in den HACS-Standardkatalog ist ein separater späterer Schritt.

Bei privaten Repositories keine PATs/Schlüssel in YAML, Download-URLs oder
Installationsskripte eintragen. Die authentifizierte GitHub-Weboberfläche für den
aktuellen privaten Download verwenden.
