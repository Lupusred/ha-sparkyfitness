# Werte aus Home Assistant nach SparkyFitness übertragen

Ab Version 0.2.0 gibt es sechs Aktionen. Sensoren bleiben Anzeigeobjekte; ihre
Zustände werden nicht automatisch zurückgeschrieben. Damit entstehen keine
Rückkopplungen zwischen eingelesenen Tageswerten und Schreibaktionen.

## Einmalige Aktivierung pro Konto

1. In SparkyFitness einen eigenen API-Schlüssel mit Schreibrechten erstellen.
   Einen bestehenden Schlüssel mit reinen Leserechten kannst du weiterverwenden,
   solange du keine Schreibaktionen benötigst.
2. In HA → Einstellungen → Geräte & Dienste → SparkyFitness → Menü des Eintrags →
   **Neu konfigurieren** den Schlüssel ersetzen. Server und Benutzer müssen gleich
   bleiben; Unique IDs bleiben erhalten. Schlüssel nicht in YAML-Automationen speichern.
3. In den Optionen dieses Kontos **Schreibaktionen aktivieren** einschalten.
   Standardmäßig und nach dem Update bestehender Einträge bleibt dies ausgeschaltet.
4. Unter **Entwicklerwerkzeuge → Aktionen** nach `sparkyfitness` suchen, die Aktion
   wählen und über das Kontofeld genau einen Integrationseintrag auswählen.

Interaktive Aufrufe benötigen einen HA-Administrator. Vertrauenswürdige
Automationen/Skripte ohne Benutzerkontext dürfen die Aktionen ebenfalls aufrufen.
Deshalb Zugriffsrechte auf Skripte, Dashboards und Automationen sorgfältig vergeben.
Jeder Aufruf prüft die aktivierte Schreiboption und die serverseitige Identität.

## Aktionen

| Aktion | Eingaben / Verhalten |
|---|---|
| `sparkyfitness.set_body_measurements` | Gewicht, Hals, Taille, Hüfte, Größe, Körperfett, Muskelmasse, Knochenmasse, Körperwasser, Schritte, Ruhepuls, **gemessener** BMR. Nur ausdrücklich gesetzte Felder werden geschrieben. |
| `sparkyfitness.record_custom_measurement` | Bestehende Kategorie-UUID und Wert in ihrer konfigurierten Einheit; Textkategorien ebenfalls möglich. Bei stündlichen Kategorien zusätzlich lokale Stunde 0–23. |
| `sparkyfitness.record_water` | `amount_ml` und eine eigene stabile `record_id`, etwa `glass-20261105-01`. Dieselbe ID aktualisiert dieselbe HA-Messung; eine andere ID ist ein weiterer Eintrag. |
| `sparkyfitness.record_sleep` | `bedtime` und `wake_time` als ISO-Zeitstempel **mit UTC-Offset**, z. B. `2026-11-04T23:00:00+01:00`. Datum ist der Aufwachtag in der konfigurierten Zeitzone. |
| `sparkyfitness.log_food` | Vorhandene `food_id`, `variant_id`, verzehrte `quantity`, deren Portionseinheit `unit` und `meal_type`. Kalorien/Makros werden aus der Lebensmittelvariante ermittelt. |
| `sparkyfitness.log_exercise` | Vorhandene `exercise_id`, `duration_minutes` und erfasste `calories_burned`. Keine Änderung einer berechneten Tagesbilanz. |

Alle Aktionen benötigen `config_entry_id`; im visuellen Aktionseditor wird das
Konto ausgewählt. `date` ist optional, Standard heute in der Integrationszeitzone.
Vergangene Tage sind erlaubt, zukünftige nicht. Dies schreibt nach SparkyFitness,
nicht rückwirkend in den Home-Assistant-Recorder. Nach Erfolg wird neu eingelesen;
bei einem Lesefehler lautet die Aktionsantwort weiterhin `saved: true`, aber
`refresh_successful: false`. Ein gültiger Schreibaufruf wird dadurch nicht wiederholt.

### Beispiel: Körpermaße

```yaml
action: sparkyfitness.set_body_measurements
data:
  config_entry_id: DEIN_INTEGRATIONSEINTRAG
  date: "2026-11-05"
  weight: 80.2
  waist: 90
  hips: 98
```

Masse in kg, Längen in cm, Prozentwerte 0–100, Puls in bpm. `steps` ist eine ganze
Zahl. `bmr` ist nur für einen extern **gemessenen** Grundumsatz (600–6000 kcal),
nicht für den von SparkyFitness berechneten Schätzwert vorgesehen. Die vorhandenen
Werte der ausdrücklich übergebenen Felder am angegebenen Tag werden ersetzt;
alle nicht übergebenen Felder bleiben unangetastet. Keine Nullwerte zum Löschen.
Garmin kann diese Tageswerte bei einer späteren eigenen Synchronisierung erneut
ändern; es gibt keinen automatischen Vorrang von HA gegenüber anderen Quellen.

Die Kategorie-UUID steht als letzter Bestandteil der Unique ID des dynamischen
Sensors (`…_custom_<UUID>`) in der Entity-Registry bzw. lässt sich in den
SparkyFitness-API-Antworten nachsehen. Lebensmittel-, Varianten- und Übungs-UUIDs
stammen aus SparkyFitness; es gibt noch keinen HA-Katalogbrowser für diese IDs.
Es werden keine neuen Lebensmittel oder Übungen automatisch angelegt.

## Wiederholungen und Grenzen

- Körpermessungen ersetzen nur explizite Felder eines Tages. Kategorien Daily/Hourly
  ersetzen den HA-Eintrag desselben Tages/Stundenfensters. Kategorien All/Unlimited
  erzeugen bei jedem Aufruf einen neuen Eintrag, auch bei identischem Wert.
- Wasser: IDs sind pro HA-Konto namensraumgebunden; keine IDs anderer Quellen
  verwenden. Für jeden neuen Trinkvorgang eine neue ID, bei Korrektur dieselbe.
- Essen und Training: jeder Aufruf erzeugt einen neuen Eintrag. Kein automatisches
  Retry bei Timeout, 5xx oder unklarer Antwort. Zuerst in SparkyFitness nachsehen,
  ob gespeichert wurde, dann bewusst erneut ausführen.
- Schlaf verwendet SparkyFitness' manuellen Endpunkt. Der Server kann manuelle
  Einträge zusammenführen sowie fehlende Phasen und Scores selbst ableiten.
  Die Integration übermittelt nur Beginn/Ende/Dauer, keine erfundenen Messphasen.
- Standardziele und berechnete verbleibende Kalorien, Tagesverbrauch, aggregierte
  Trainingsdauer/-anzahl und Schlafbewertungen bleiben schreibgeschützt. Vorhandene
  selbst definierte Kategorien dürfen Messwerte erhalten; es gibt keinen generischen
  Endpunkt- oder JSON-Payload-Durchgriff.
- Vorhandene Einträge löschen, Lebensmitteldefinitionen ändern, Trainingspläne
  bearbeiten und Zielzeiträume umschreiben sind nicht Bestandteil dieser Version.
- Keine automatische Rückübertragung aller Sensoren. Automationen nur auf die
  echte Quellmessung ausrichten, nicht auf den von SparkyFitness gelesenen Sensor.

Alle bisherigen Schreibtests verwenden synthetische Daten. Ein Produktionstest
wurde nicht durchgeführt. Ersten Test bewusst mit einem einzelnen gewählten Wert
selbst ausführen und das Ergebnis in SparkyFitness kontrollieren.
