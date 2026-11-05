# Installation im vorhandenen Unraid-Container

Die Entwicklung hat keine produktiven Container, Volumes oder Konfigurationsdateien
verändert. Voraussetzung: Home Assistant Core ab 2026.2, SparkyFitness mit der
untersuchten 1.11.0-API und Netzwerkzugriff von Home Assistant auf SparkyFitness.

## Vorbereitungen

1. In Unraid → Docker → Home-Assistant-Container → Edit die bestehende Zuordnung
   des Containerpfads `/config` ablesen. Den tatsächlichen Hostpfad verwenden,
   etwa `/mnt/user/appdata/home-assistant`; nicht blind diesen Beispielpfad übernehmen.
2. Eine Sicherung des bestehenden Konfigurationsverzeichnisses erstellen.
3. In SparkyFitness → Settings → API Key Management einen eigenen API-Schlüssel
   mit **Read-only**-Scope für den Lesebetrieb und geeigneter Ablaufzeit erzeugen. Die Bezeichnung kann
   „Home Assistant“ sein. Schlüssel direkt in HA eingeben, niemals in Git/Chat.
4. Die SparkyFitness-Web-URL prüfen. Im HA-Container bezeichnet `localhost` den
   HA-Container, nicht SparkyFitness. Meist ist die Unraid-LAN-IP mit dem
   veröffentlichten SparkyFitness-Webport richtig; alternativ Container-DNS im
   gemeinsamen benutzerdefinierten Docker-Netzwerk. Keine Port-/Volume-Änderung
   allein für die Integration erforderlich.

## HACS

1. Falls HACS bereits vorhanden ist: HACS öffnen → Menü → Benutzerdefinierte
   Repositories → `https://github.com/Lupusred/ha-sparkyfitness` hinzufügen,
   Kategorie **Integration**. Dieser Standardweg setzt ein öffentlich erreichbares
   Repository voraus; das aktuelle Repository ist privat. Bis zur bewussten
   Veröffentlichung die manuelle Installation bzw. die GitHub-Artefakte verwenden.
2. SparkyFitness herunterladen. Für den späteren öffentlichen HACS-Weg siehe DISTRIBUTION.md.
3. Home Assistant über seine Neustartfunktion neu starten; falls erforderlich
   den bestehenden HA-Container in Unraid neu starten. Kein Container-Neuaufbau.

## Manuell

1. Im ermittelten HA-Konfigurationsverzeichnis `custom_components` anlegen, falls
   noch nicht vorhanden. Andere Integrationen beibehalten.
2. Den vollständigen Ordner `custom_components/sparkyfitness` aus diesem Projekt
   nach `<HA-Konfigurationsverzeichnis>/custom_components/sparkyfitness` kopieren.
   Bei einem Update vorher die vorhandene SparkyFitness-Version sichern.
3. Kontrolle im Container: `/config/custom_components/sparkyfitness/manifest.json`,
   `__init__.py`, `api.py`, `config_flow.py`, `const.py`, `coordinator.py`, `data.py`,
   `sensor.py`, `services.py`, `services.yaml`, `strings.json`,
   `translations/de.json`, `translations/en.json` und `brand/`
   müssen vorhanden sein. Keine zusätzliche Verschachtelung `ha-sparkyfitness`.
4. Home Assistant neu starten. Keine YAML-Konfiguration erforderlich.

## Einrichtung und Prüfung

Unter Einstellungen → Geräte & Dienste → Integration hinzufügen → SparkyFitness
Server-URL und API-Schlüssel eingeben. Pro Konto einen eigenen Schlüssel und
Integrationseintrag verwenden. In den Optionen Intervall und Zeitzone einstellen;
die Zeitzone muss zum SparkyFitness-Profil passen.

Unter dem angelegten Gerät die Entitäten prüfen. Gewichts-/Kaloriensensoren mit
SparkyFitness vergleichen, einschließlich des ausgewählten Tages und der Einheiten.
Eine neue Messkategorie sollte beim nächsten Poll erscheinen. `unknown` bedeutet
fehlender/ungültiger Wert; `unavailable` bedeutet fehlgeschlagene Aktualisierung,
entferntes Feld oder noch nicht aktualisierter Tageswechsel. Eine leere Kategorie
kann einen Sensor ohne Wert erzeugen. Garmin-Werte erscheinen nur, wenn sie zuvor
in SparkyFitness importiert wurden.

## Fehlerdiagnose

- Integration nicht sichtbar: Ordnerpfad, manifest.json und HA-Neustart prüfen.
- Anmeldung fehlgeschlagen: Schlüssel, Ablaufzeit, Leseberechtigung und Web-URL
  prüfen. Keine Garmin-Anmeldedaten verwenden.
- TLS-Fehler: gültiges Zertifikat bzw. korrekte Vertrauenskette einrichten. Es gibt
  keinen Schalter zum Abschalten der Zertifikatsprüfung. Lokales HTTP ist für ein
  vertrauenswürdiges Heimnetz möglich; dort werden Schlüssel unverschlüsselt übertragen.
- Umleitung/HTML statt API-JSON: endgültige Serveradresse verwenden, vorgeschaltete
  Login-Seiten und Reverse-Proxy-Konfiguration prüfen. Umleitungen werden abgelehnt.
- HTTP 429: Intervall erhöhen; weitere API-Verbraucher und Serverlimits prüfen.
- Keine Sensoren: Serverversion und API-Verfügbarkeit prüfen; 404-Endpunkte werden
  als nicht unterstützt behandelt. Nicht alle alten Versionen sind kompatibel.
- Nach Ausfall: der nächste reguläre Poll versucht erneut; abgelehnte Schlüssel
  über den von Home Assistant angebotenen erneuten Anmeldedialog ersetzen.
- Relevante HA-Logs sind unter Einstellungen → System → Protokolle sichtbar.
  Vor Weitergabe prüfen/redigieren; keine kompletten .storage-Dateien senden.

## Updates und Rückkehr

HACS zeigt veröffentlichte Versionen an; herunterladen und HA neu starten.
Bei manueller Installation nur den Integrationsordner durch die neue vollständige
Version ersetzen, dann neu starten. Release Notes und Mindestversionen prüfen.
Für eine Rückkehr den gesicherten Integrationsordner wiederherstellen und HA neu
starten. Einträge nicht unnötig löschen: sonst können Zuordnungen/Entity IDs ändern.

## Begrenzter Live-Test (noch ausstehend)

Zunächst werden nur benötigt: genaue HA- und SparkyFitness-Versionen, verwendete
URL-Art (LAN-IP/Container-DNS/Reverse-Proxy, keine Zugangsdaten), Profilzeitzone
und die gewünschten Datenfamilien. Den Schlüssel ausschließlich in HA eingeben.
Danach lokal Verbindung, zwei bis drei ausgewählte Werte/Einheiten, eine neue
Kategorie, einen Poll und einen vorübergehenden Verbindungsfehler prüfen. Zur
Rückmeldung genügen Erfolg/Fehlerklasse und optional redigierte synthetische
Antwortstrukturen. Keine Gesundheitswerte oder vollständigen Logs erforderlich.

## Schreiben ab 0.2.0

Der bestehende Lesebetrieb bleibt nach einem Update erhalten. Schreibaktionen
sind pro Konto ausgeschaltet. Aktivierung, Austausch des API-Schlüssels über
„Neu konfigurieren“ und Beispiele stehen in [WRITING.md](WRITING.md).
Keine Automationen auf Basis der bereits eingelesenen SparkyFitness-Sensoren
pauschal zurückschreiben lassen.
