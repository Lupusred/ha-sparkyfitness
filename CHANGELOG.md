# Änderungen

## 0.2.0 — 2026-11-05

Erste öffentliche Veröffentlichung für die Installation als HACS Custom Repository.

- UI-Einrichtung und getrennte SparkyFitness-Konten mit stabilen Entitäts-IDs.
- Ernährung, Ziele, Körpermessungen, Aktivität, Schlaf und dynamische Kategorien.
- Automatische Aktualisierung, Zeitzonen und Tageswechselbehandlung.
- Sechs optionale Schreibaktionen für Messungen und Tagebucheinträge; standardmäßig
  ausgeschaltet, mit Kontoprüfung, Administratorrechten und validierten Eingaben.
- Schlüsselwechsel ohne Löschen des Kontos über „Neu konfigurieren“.
- Offizielles Logo mit vollständigen Upstream-Lizenzhinweisen.
- Deutsche/englische UI, GitHub-Dokumentation, Installationspaket und Sicherheitsbericht.
- 80 synthetische Tests. Schreibfunktionen noch ohne produktiven Live-Test;
  getestete Basis: HA 2026.2.3 und SparkyFitness-API 1.11.0.

Bestehende manuelle Installationen können zu HACS wechseln. Einträge nicht löschen;
Integrationsdateien über HACS aktualisieren und Home Assistant neu starten.

## 0.1.0 — Entwicklungsversion

Erste lesende Integration. Manuelle Installation und Lesebetrieb wurden vom ersten
Benutzer bestätigt. Kein früherer öffentlicher Release-Tag verfügbar.
