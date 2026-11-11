# Prüfung offener Pull Requests — 2026-11-11

Auftrag: offene PRs prüfen und bearbeiten. Aktuelle Einschränkung: nichts
veröffentlichen. Keine Merges, Releases oder produktiven Änderungen durchgeführt.
Alle sechs PRs zielen auf develop/sparkyfitness, nicht main.

| PR | Änderung | Befund |
| --- | --- | --- |
| #2 | actions/checkout v4 → v7 in Validate und Release | Tests/Hassfest erfolgreich; HACS-Nachprüfung angefordert. Release-Upload mit neuer Action noch nicht separat ausgeführt. |
| #3 | actions/upload-artifact v4 → v7 | Tests einschließlich Paketbau/Upload, HACS und Hassfest erfolgreich. |
| #4 | actions/setup-python v5 → v7 | Python bleibt 3.13; Tests/Hassfest erfolgreich, HACS-Nachprüfung angefordert. |
| #5 | HA-Testbibliothek 0.13.316 → 0.13.375 | Nicht unverändert übernehmen: neue Bibliothek benötigt Python >=3.14; CI verwendet 3.13. Installation scheitert vor den Tests. |
| #6 | Bandit 1.8.6 → 1.9.4 | Tests und Sicherheitsprüfung erfolgreich; HACS-Nachprüfung angefordert. |
| #7 | Ruff 0.15.0 → 0.17.3 | Tests, Lint und Formatprüfung erfolgreich; HACS-Nachprüfung angefordert. |

Die alten roten HACS-Ergebnisse wurden anhand des Jobprotokolls auf fehlende
Repository-Topics zurückgeführt. Die Topics wurden bei der Veröffentlichung
bereits ergänzt. Fehlgeschlagene Jobs der Läufe 42178157900, 42178169111,
42178204991 und 42178222866 erneut gestartet; Testergebnisse nicht durch
Deaktivieren von Prüfungen verändert.

PR #5 ist kein Laufzeitfehler der Integration. Ein isoliertes Bibliotheksupdate
kann unter Python 3.13 nicht funktionieren. Empfehlung: diesen Versionssprung
zurückstellen und die Modernisierung separat als Testmatrix vorbereiten:
Python 3.13 / bisherige HA-Testbasis weiter prüfen; Python 3.14 / neue HA-Testbasis
zusätzlich installieren und testen. Nicht allein die bestehende Python-Version
erhöhen, da damit der Nachweis für die dokumentierte Mindestversion entfiele.
Keine Änderung an der Mindestversion oder an requirements-dev.txt vorgenommen.

Nächste Schritte nach Freigabe: geprüfte Wartungs-PRs einzeln übernehmen und
kombinierten Entwicklungsstand testen. PR #5 erst mit abgestimmter Testmatrix
übernehmen. Keine neue Integrationsversion nur für CI-/Entwicklungswerkzeuge nötig.

Abschluss: Alle vier erneut gestarteten Läufe sind erfolgreich abgeschlossen.
Damit haben PR #2, #3, #4, #6 und #7 erfolgreiche Tests, Hassfest und HACS.
Die unveränderten Testjobs stammen aus den ursprünglichen Läufen; erneut ausgeführt
wurden nur die zuvor fehlgeschlagenen HACS-Jobs. Kombinierte Updates noch nicht getestet.
