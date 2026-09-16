# API-README: sichere Anbindung fuer Landesverbaende

Diese Datei erklaert in normaler Sprache, was die API macht, warum sie fuer den
DBFV-Inhaber sicher ist und warum sie den Arbeitsaufwand nicht erhoeht, sondern
reduziert. Die technische Detaildokumentation steht in `API.md`.

## Kurzfassung fuer den DBFV

Die API ist eine sichere Schnittstelle zwischen dem bestehenden DBFV-
Lizenzsystem und berechtigten Landesverbaenden, zum Beispiel dem DBFV NRW.

Der wichtige Punkt: Der Landesverband arbeitet nicht an der Datenbank vorbei.
Ein Antrag, der ueber die NRW-Webseite eingeht, wird weiterhin im DBFV-
Lizenzsystem angelegt. Das DBFV-System bleibt also das fuehrende System.

Was sich verbessert:

- Mitglieder koennen ihre Lizenz direkt in ihrem Landesverbands-Portal
  beantragen und bezahlen.
- Der Antrag landet automatisch im DBFV-Lizenzsystem.
- Die Zahlung wird am Antrag im DBFV-System dokumentiert.
- Die bekannten Benachrichtigungs-Mails an Verwalter, Landesverband, Studio und
  Antragsteller werden weiter verschickt.
- Der DBFV-Verwalter muss nicht manuell Daten aus E-Mails oder Listen
  uebertragen.

## Erklaerung fuer jemanden ohne Technik-Hintergrund

Man kann sich die API wie einen verschlossenen Briefkasten vorstellen.

Der DBFV stellt fuer NRW einen eigenen Schluessel aus. Mit diesem Schluessel
darf NRW nur bestimmte Dinge tun, zum Beispiel Starterlizenz-Antraege fuer NRW
einreichen. NRW kann damit nicht einfach alles im System sehen oder veraendern.

Wenn ein Athlet auf der NRW-Webseite seine Lizenz kauft, passiert folgendes:

1. Der Athlet gibt seine Daten auf der NRW-Webseite ein.
2. Die NRW-Webseite sendet den Antrag ueber die geschuetzte API an das
   DBFV-Lizenzsystem.
3. Das DBFV-Lizenzsystem speichert den Antrag.
4. Falls die Zahlung bereits bei NRW eingegangen ist, wird diese Zahlung direkt
   am Antrag vermerkt.
5. Die normalen E-Mails gehen raus: an die DBFV-Verwalter, den Landesverband,
   ggf. das Studio und den Antragsteller.
6. Im DBFV-System ist sichtbar, dass der Antrag ueber die API kam und welcher
   API-Key ihn angelegt hat.

Das bedeutet: Der DBFV-Chef verliert keine Kontrolle. Im Gegenteil: Er bekommt
sauberere Daten, schnellere Ablaeufe und weniger manuelle Rueckfragen.

## Warum das dem DBFV-Inhaber nicht schadet

Die API gibt keine Generalvollmacht.

Jeder API-Key hat einzeln waehlbare Rechte:

- welcher Landesverband erlaubt ist,
- ob Starter-Antraege angelegt werden duerfen,
- ob Studio-, internationale oder Kampfrichter-Antraege angelegt werden duerfen,
- ob Zahlungen eingetragen werden duerfen,
- ob Lizenzen abgefragt werden duerfen,
- ob ein Massenexport erlaubt ist,
- ob Roh-Antragsdaten gelesen werden duerfen,
- ob ein Key bundesweiten Systemzugriff hat.

Ein NRW-Key kann also so eingestellt werden:

- nur NRW,
- Starter-Antraege anlegen,
- Zahlungen registrieren,
- Lizenzstatus gezielt pruefen,
- kein bundesweiter Zugriff,
- kein Zugriff auf fremde Landesverbaende.

Dadurch kann NRW nicht Hessen, Bayern oder Berlin einsehen. Auch wenn jemand die
URL eines fremden Antrags kennt, bekommt er die Daten nicht, weil die
Verbandsgrenze serverseitig erzwungen wird.

## Warum der DBFV weniger Arbeit hat

Ohne API:

- Mitglied zahlt oder beantragt irgendwo,
- Daten muessen per E-Mail, CSV oder manuell weitergegeben werden,
- jemand muss pruefen, ob Zahlung und Antrag zusammenpassen,
- es entstehen Rueckfragen,
- Zahlungsvermerke liegen eventuell im NRW-System, aber nicht im DBFV-System.

Mit API:

- der Antrag kommt direkt strukturiert im DBFV-System an,
- die Zahlung wird direkt am Antrag gespeichert,
- die bekannten E-Mails gehen automatisch raus,
- Verwalter sehen schneller, was passiert ist,
- NRW kann Mitglieder besser fuehren, ohne den DBFV aus dem Prozess zu nehmen.

Das Ziel ist also nicht, Arbeit auf den DBFV zu verschieben. Das Ziel ist, die
Arbeit, die heute verteilt und manuell passiert, geordnet ins bestehende System
zu bringen.

## Was die API aktuell kann

### 1. Rechte und Optionen anzeigen

Ein Frontend kann abfragen, was sein API-Key darf:

- `GET /api/v1/capabilities/`

Damit weiss die NRW-Webseite zum Beispiel:

- darf dieser Key Starter-Antraege anlegen?
- darf dieser Key Zahlungen registrieren?
- welche Landesverbaende sind erlaubt?
- darf dieser Key Lizenzstatus abfragen?

Ausserdem kann ein Frontend erlaubte Formularoptionen laden:

- `GET /api/v1/submissions/options/`

Die Antwort enthaelt nur das, was der Key sehen darf, zum Beispiel nur NRW-
Studios fuer einen NRW-Key.

### 2. Lizenzstatus pruefen

Ein berechtigter Key kann gezielt pruefen, ob eine Lizenz existiert:

- `POST /api/v1/licenses/lookup/`

Das ist datensparsam. Es werden keine Personenlisten ausgegeben, sondern nur,
ob eine passende gueltige Lizenz gefunden wurde.

### 3. Gueltige Lizenzen exportieren

Ein besonders berechtigter Key kann gueltige Lizenzen exportieren:

- `GET /api/v1/licenses/valid/`

Das braucht zwei Rechte:

- `sensitive_access`
- `allow_export_licenses`

Ein normaler NRW-Frontend-Key braucht diesen Export in der Regel nicht.

### 4. Antraege fachlich anlegen

Neue Antraege werden nicht ueber generisches Datenbank-Schreiben angelegt,
sondern ueber eigene Fach-Endpunkte:

- `POST /api/v1/submissions/starter/`
- `POST /api/v1/submissions/international/`
- `POST /api/v1/submissions/gym/`
- `POST /api/v1/submissions/judge/`

Diese Endpunkte machen mehr als nur speichern:

- Verbandsgrenze pruefen,
- Pflichtdaten validieren,
- lokalen Antragsteller-User zuordnen oder anlegen,
- Zahlungsdaten speichern, falls erlaubt,
- API-Herkunft am Antrag speichern,
- externe Referenz gegen doppelte Uebermittlung speichern,
- normalen Mailworkflow ausloesen.

## Was beim NRW-Lizenzkauf passiert

Beispiel: Ein Athlet kauft eine Starterlizenz auf der DBFV-NRW-Webseite.

Der NRW-Flow kann dann diese Daten an die API senden:

- Athletendaten,
- Studio,
- Kategorie,
- Zustimmung zu Regeln und Datenschutz,
- Zahlung: bezahlt, Betrag, Referenz, Zeitpunkt.

Das DBFV-System legt daraus einen normalen Starterlizenz-Antrag an. Der Antrag
bekommt zusaetzlich:

- `created_via_api = True`
- den API-Key-Prefix als Herkunftsnachweis,
- eine `external_reference` aus dem NRW-System, damit ein Timeout nicht zu
  Doppelantraegen fuehrt,
- Zahlungsstatus,
- Zahlungsreferenz,
- Zahlungsbetrag,
- Zahlungszeitpunkt.

Danach gehen automatisch die Mails raus. Der DBFV-Verwalter wird also nicht
umgangen, sondern schneller informiert.

## Warum das sicherer ist als E-Mail oder CSV

E-Mail und CSV sind ungenau:

- Dateien koennen falsch weitergeleitet werden,
- Spalten koennen verrutschen,
- Zahlung und Antrag koennen getrennt landen,
- jemand muss manuell pruefen,
- es gibt oft keine klare technische Grenze pro Landesverband.

Die API ist kontrollierter:

- jeder Zugriff braucht einen API-Key,
- jeder Key hat exakt gesetzte Rechte,
- jeder Key kann auf Landesverbaende begrenzt werden,
- ungueltige Zugriffe werden abgelehnt,
- zu viele Anfragen werden begrenzt,
- API-Antraege werden am Antrag markiert,
- Zahlungen werden am Antrag gespeichert,
- API-Zugriffe sind im Django-Admin als Verlauf einsehbar,
- der DBFV bleibt System of Record.

## Welche Rechte der Verwalter setzen kann

Im Django-Admin koennen pro API-Key unter anderem diese Rechte gesetzt werden:

| Recht | Bedeutung |
|---|---|
| `allowed_states` | Welche Landesverbaende der Key sehen/bearbeiten darf |
| `federal_access` | Bundes-/Systemzugriff ueber alle Landesverbaende |
| `allow_submit_starter` | Starterlizenz-Antraege anlegen |
| `allow_submit_international` | Internationale Antraege anlegen |
| `allow_submit_gym` | Studio-/Vereinsantraege anlegen |
| `allow_submit_judge` | Kampfrichter-Antraege anlegen |
| `allow_register_payments` | Zahlungsdaten beim Antrag speichern |
| `allow_lookup_licenses` | Einzelne Lizenz gezielt pruefen |
| `allow_export_licenses` | Gueltige Lizenzen als Liste exportieren |
| `allow_read_submissions` | Roh-Antragsdaten lesen |
| `sensitive_access` | Zugriff auf besonders sensible Daten |
| `write_allowed` | Generisches Schreiben auf erlaubten Stammdaten |
| `allowed_ips` | Optional: nur bestimmte Server-IP erlauben |

Fuer die NRW-Webseite ist typischerweise kein bundesweiter Zugriff noetig.

## Kontrolle im Admin: API-Zugriffe

Im Django-Admin gibt es einen Bereich **API-Zugriffe**.

Dort sieht der Betreiber:

- wann ein API-Zugriff stattgefunden hat,
- welcher API-Key-Prefix genutzt wurde,
- von welcher IP-Adresse die Anfrage kam,
- welche API-Route aufgerufen wurde,
- ob der Zugriff erfolgreich war oder abgelehnt wurde.

Bewusst nicht gespeichert werden:

- der geheime API-Key,
- Formularinhalte,
- Zahlungsdaten,
- Suchparameter aus URLs.

Damit hat der DBFV einen nachvollziehbaren Verlauf, ohne unnoetig
personenbezogene Inhalte in ein Log zu kopieren. Das hilft bei Rueckfragen wie:
„Hat NRW heute Antraege uebermittelt?“ oder „Wurde ein fremder Verband
abgefragt?“.

## Empfohlene NRW-Key-Konfiguration

Fuer den geplanten NRW-Lizenzkauf:

- `allowed_states`: NRW
- `federal_access`: aus
- `allow_submit_starter`: an
- `allow_register_payments`: an
- `allow_lookup_licenses`: optional an
- `allow_submit_gym`: nur wenn NRW darueber Studio-/Vereinsantraege stellen soll
- `allow_submit_judge`: aus, solange nicht benoetigt
- `allow_submit_international`: aus, solange nicht benoetigt
- `allow_export_licenses`: aus, wenn kein Massenexport gebraucht wird
- `allow_read_submissions`: aus, wenn die NRW-Webseite keine Roh-Antragslisten braucht
- `sensitive_access`: nur an, wenn wirklich benoetigt
- `allowed_ips`: wenn moeglich auf den NRW-Server begrenzen

Das ist ein enger, nachvollziehbarer Zugriff.

## Was bewusst nicht passiert

- NRW bekommt keinen automatischen Zugriff auf andere Landesverbaende.
- NRW bekommt keinen Vollzugriff, nur weil ein API-Key existiert.
- Antraege werden nicht heimlich nur in NRW gespeichert.
- Der DBFV-Mailworkflow wird nicht umgangen.
- Zahlungen verschwinden nicht in einem separaten NRW-System, sondern werden am
  DBFV-Antrag dokumentiert.

## Grenzen und offene Punkte

Diese API schafft die Grundlage fuer den sicheren NRW-Flow. Es gibt trotzdem
Punkte, die man vor dem produktiven Start organisatorisch klaeren sollte:

- Welche Zahlungsreferenz soll verbindlich verwendet werden?
- Welche externe Referenz nutzt NRW pro Bestellung oder Zahlung?
- Welche Zahlungssumme ist pro Lizenztyp fachlich korrekt?
- Soll der DBFV-Verwalter API-Zahlungen automatisch als ausreichend betrachten
  oder zusaetzlich freigeben?
- Welche Server-IP bekommt der NRW-Key?
- Wer darf im Admin neue API-Keys ausstellen?
- Wie oft werden Keys gewechselt?

Das sind keine Gruende gegen die API. Das sind normale Betriebsfragen, die
durch diese saubere Schnittstelle ueberhaupt erst ordentlich geregelt werden
koennen.

## Einfache Botschaft fuer den DBFV-Chef

Die API nimmt dem DBFV keine Kontrolle weg.

Sie sorgt dafuer, dass NRW seine Mitglieder moderner bedienen kann, waehrend
alle Antraege und Zahlungen weiterhin im DBFV-System dokumentiert werden.

Der DBFV bekommt:

- weniger manuelle Arbeit,
- schnellere Informationen,
- bessere Nachvollziehbarkeit,
- weniger Medienbrueche,
- klare Rechte pro Landesverband,
- automatische Benachrichtigung wie bisher.

Kurz: NRW kann schneller arbeiten, ohne dass der DBFV die Hoheit ueber das
Lizenzsystem verliert.
