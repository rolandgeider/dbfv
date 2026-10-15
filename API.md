# DBFV REST-API

Für eine nicht-technische Erklärung, insbesondere für Vorstand,
Geschäftsstelle und Landesverbände, siehe `API-README.md`.

## Warum diese API

Das Antragssystem des DBFV e.V. verwaltet Starter-, Studio- und
Kampfrichterlizenzen. Bislang lag der Datenzugriff ausschließlich in der
Weboberfläche und im Django-Admin.

Der **DBFV NRW** (Landesverband) benötigt **programmatischen Zugriff** auf diese
Daten, um Lizenzgültigkeiten von NRW-Athleten zu prüfen (z. B. bei der
Wettkampfanmeldung über die NRW-Website) und Anträge inklusive Zahlungsvermerk
direkt im Lizenzsystem anzulegen. Diese API schafft dafür eine definierte,
abgesicherte und datensparsame Schnittstelle. Das Lizenzsystem bleibt das
führende System; die API arbeitet nicht an ihm vorbei.

## Authentifizierung

Jeder Zugriff braucht einen **API-Key** im HTTP-Header:

```
Authorization: Api-Key <PREFIX.SCHLUESSEL>
```

- Ohne gültigen Key: `403 Forbidden`.
- Der Key wird als Hash gespeichert; das Secret ist nur bei der Erstellung
  sichtbar.
- Jedes Recht ist ein eigenes Flag am Key (siehe Rechte-Matrix). Ein neuer Key
  ohne Flags darf nur Stammdaten (Studios, Bundesländer, Länder) lesen.

### Landesverbandsgrenze

- `allowed_states` beschränkt einen Key auf die ausgewählten Landesverbände.
  Ein NRW-Key sieht und schreibt nur NRW-Daten (Bundesland, Studios,
  Benutzerprofile, Anträge, Lizenz-Export/-Lookup, Formularoptionen).
  Landesverbands-Keys brauchen mindestens einen Eintrag in `allowed_states`.
- **Bundesweite Ressourcen** sind für Landesverbands-Keys grundsätzlich
  unsichtbar (leere Liste, Detail `404`) und unveränderbar (`403`):
  Bankkonten (`State.bank_account` ist ein von mehreren Verbänden geteiltes
  Konto), Manager-E-Mails (erhalten jede Antragsbenachrichtigung bundesweit)
  und der Mail-Cron.
- Landesverbands-Keys dürfen Bundesländer weder anlegen, ändern noch löschen
  (Löschen würde per `CASCADE` alle Studios, Profile und Anträge des Verbands
  mitreißen). Länder und Benutzerprofile können sie lesen, aber nur
  Bundes-Keys schreiben: `UserProfile.type` vergibt Bundesverbandsrechte, und
  ein Profil darf nicht aus dem Verband herausgeschoben werden.
- **Bundes-/Systemzugriff:** Verbandsübergreifender Zugriff ist nur mit
  `federal_access=True` möglich. Neue Keys ohne `federal_access` und ohne
  `allowed_states` sehen keine verbandsgebundenen Daten.

### Rechte-Matrix

| Flag | Wirkung |
|---|---|
| `allowed_states` | Landesverbände, auf die der Key begrenzt ist |
| `federal_access` | Bundes-/Systemzugriff über alle Verbände, inkl. Bankkonten, Manager-E-Mails, Mail-Cron |
| `allow_lookup_licenses` | `POST /licenses/lookup/` (gezielte, datensparsame Gültigkeitsprüfung) |
| `allow_lookup_all_states` | Lookup prüft auch Lizenzen anderer Landesverbände (Gaststarter bei NRW-Wettkämpfen); Antwort bleibt „gültig ja/nein" |
| `allow_export_licenses` | `GET /licenses/valid/` (Massen-Export; zusätzlich `sensitive_access` nötig) |
| `allow_read_submissions` | Roh-Anträge über `/submission*/` lesen (zusätzlich `sensitive_access` nötig) |
| `allow_submit_starter` / `_international` / `_gym` / `_judge` | Anträge über `/submissions/<typ>/` anlegen |
| `allow_register_payments` | `payment`-Block beim Anlegen eines Antrags speichern |
| `sensitive_access` | Zugriff auf personen-/finanzbezogene Ressourcen: Benutzerprofile, Roh-Anträge, Massen-Export; bei Bundes-Keys auch Bankkonten, Manager-E-Mails, Mail-Cron |
| `write_allowed` | Generisches Schreiben (`POST`/`PUT`/`PATCH`) auf erlaubten Ressourcen; `DELETE` braucht zusätzlich `sensitive_access` |
| `allowed_ips` | Optionale IP-/CIDR-Allowlist (leer = keine Einschränkung) |

Die generischen `submission*`-Ressourcen sind bewusst **read-only**. Anträge
werden ausschließlich über die Fach-Endpunkte unter `/submissions/…/` angelegt,
damit Verbandsgrenze, Zahlung, Idempotenz und Mailversand nicht umgangen werden.

### Rate-Limits und Zugriffsprotokoll

- **Pro API-Key:** 1000 Anfragen/Stunde (DRF-Throttle `apikey`).
- **Vor der Key-Prüfung** gilt zusätzlich ein IP-Limit von 120 Anfragen/Minute
  (`API_PREAUTH_RATE_LIMIT`), damit auch ungültige oder wechselnde Keys
  begrenzt werden. Es gilt für alle Pfade unter `/api/v1/`, auch für
  Schema und Swagger-UI.
- Beide Limits zählen im Django-Cache. In Deployments mit mehreren Prozessen
  (gunicorn-Worker) muss ein **gemeinsamer Cache** (`CACHES`, z. B.
  Datenbank-Cache oder Redis) konfiguriert sein, sonst zählt jeder Prozess für
  sich.
- Jeder API-Zugriff wird im Logger `dbfv.audit` und als `APIAccessLog`
  (Django-Admin **API-Zugriffe**) festgehalten: Zeit, Key-Prefix (max. 8
  Zeichen), Client-IP, Methode, Pfad ohne Query, Status. `401`/`403`/`429` und
  Key-Widerrufe werden als Warnung geloggt. **Nicht** gespeichert werden
  Key-Secret, Request-Body, Zahlungsdaten und Query-Parameter (mögliche
  Suchdaten).

### IP-Allowlist und Client-IP-Ermittlung

Optional lässt sich ein Key auf feste Quell-IPs beschränken (Feld `allowed_ips`,
kommagetrennte IPs oder CIDR-Bereiche). Passt die Anfrage-IP nicht, antwortet
die API mit `403`. Für Server-zu-Server-Zugriffe ist das die richtige
Zusatzsicherung; ein `Origin`-Header greift nur bei Browsern.

`X-Forwarded-For` ist client-fälschbar und wird **standardmäßig ignoriert**
(`API_TRUSTED_PROXY_COUNT = 0`, es zählt `REMOTE_ADDR`). Läuft die Anwendung
hinter einem oder mehreren vertrauenswürdigen Reverse-Proxies, wird
`API_TRUSTED_PROXY_COUNT` auf deren Anzahl gesetzt; dann wird der entsprechende
Eintrag von rechts aus der `X-Forwarded-For`-Kette genommen. Ist die Kette
kürzer als erwartet, wird fail-closed abgelehnt. Der Proxy muss eingehende
`X-Forwarded-For`-Header überschreiben, nicht anhängen. Ohne diese Einstellung
sieht die Anwendung hinter einem Proxy nur dessen IP: die Allowlist greift dann
nie, und das Pre-Auth-Limit gilt für alle Clients gemeinsam.

### Key anlegen

Im Django-Admin unter **API-Keys**, oder per Shell:

```python
from api.models import ScopedAPIKey

obj, key = ScopedAPIKey.objects.create_key(
    name="nrw-website",
    allow_submit_starter=True,     # Starteranträge anlegen
    allow_register_payments=True,  # Zahlung aus dem NRW-Frontend übernehmen
    allow_lookup_licenses=True,    # gezielte Lizenzprüfung
    allow_lookup_all_states=True,  # auch Gaststarter anderer Verbände prüfen
    allowed_ips="203.0.113.0/24",  # optional
)
obj.allowed_states.add(nrw_state)  # Pflicht für Landesverbands-Keys
print(key)  # wird nur EINMAL angezeigt; danach ist nur der Hash gespeichert
```

Das öffentliche Formular „API-Key beantragen" (Footer-Link, `/api-key/anfrage`)
schickt eine Anfrage an die Manager-Adressen und ist auf fünf POST-Anfragen pro
Stunde und Client-IP begrenzt (`API_KEY_REQUEST_RATE_LIMIT`).

## Endpunkte

Basis: `/api/v1/`

| Pfad | Zweck | Nötige Rechte |
|---|---|---|
| `GET /capabilities/` | Rechte und erlaubte Verbände des Keys | gültiger Key |
| `GET /submissions/options/` | Formularoptionen (Verbände, aktive Studios, Länder, Kategorien, Zahlungsstatus) | gültiger Key |
| `POST /submissions/starter/` | Starterantrag anlegen | `allow_submit_starter` |
| `POST /submissions/international/` | Internationalen Antrag anlegen | `allow_submit_international` |
| `POST /submissions/gym/` | Studioantrag anlegen | `allow_submit_gym` |
| `POST /submissions/judge/` | Kampfrichterantrag anlegen | `allow_submit_judge` |
| `POST /licenses/lookup/` | Gültigkeit einer Person prüfen, ohne Personendaten zurückzugeben | `allow_lookup_licenses` |
| `GET /licenses/valid/` | Massen-Export gültiger Lizenzen | `sensitive_access` + `allow_export_licenses` |
| `/gym/`, `/state/`, `/country/` | Stammdaten, CRUD | lesen: gültiger Key; schreiben: `write_allowed`; State und Country nur mit `federal_access` änderbar |
| `/userprofile/` | Benutzerprofile | lesen: `sensitive_access`; schreiben: zusätzlich `federal_access` + `write_allowed` |
| `/submissionstarter/`, `/submissioninternational/`, `/submissiongym/`, `/submissionjudge/` | Roh-Anträge, **read-only** | `sensitive_access` + `allow_read_submissions` |
| `/bankaccount/`, `/manageremail/`, `/emailcron/` | Bundesweite Ressourcen, CRUD | `federal_access` + `sensitive_access` (+ `write_allowed`) |
| `GET /schema/`, `/docs/`, `/redoc/` | OpenAPI-Schema, Swagger-UI, ReDoc | öffentlich (nur Pre-Auth-IP-Limit) |

Generische Listen sind paginiert (`PAGE_SIZE = 50`) und unterstützen
`?feld=wert` (exakter Filter auf direkte Felder), `?search=` und `?ordering=`.
Bei Landesverbands-Keys werden Listen und Details automatisch gefiltert;
fremde Detail-URLs antworten `404`, Schreibversuche auf fremde Verbandsdaten
`403`.

### Beispiel

```bash
curl -H "Authorization: Api-Key 2VvDXE8I.xxxxxxxx" \
     https://lizenz.example.org/api/v1/capabilities/
```

## Capabilities

```
GET /api/v1/capabilities/
```

```json
{
  "key_prefix": "2VvDXE8I",
  "federal_access": false,
  "states": [{ "id": 10, "name": "Nordrhein-Westfalen", "short_name": "NRW" }],
  "permissions": {
    "submit_starter": true,
    "submit_international": false,
    "submit_gym": false,
    "submit_judge": false,
    "register_payments": true,
    "lookup_licenses": true,
    "lookup_all_states": true,
    "export_licenses": false,
    "read_submissions": false,
    "sensitive_access": false,
    "write_allowed": false
  }
}
```

Ein Frontend kann damit Flows ausblenden, ohne Rechte zu erraten.

## Antrags-Endpunkte mit Zahlung

Die Fach-Endpunkte legen Anträge so an, dass der bestehende Workflow erhalten
bleibt:

- Der Antrag gehört einem **technischen Benutzer je API-Key**
  (`api:<hex-kodierter PREFIX>`, inaktiv, ohne Passwort und E-Mail). Dieser
  Namensraum ist über die öffentliche Registrierung nicht zugänglich.
  Vorhandene `api-<PREFIX>`-Konten werden nur bei exaktem Namen, Inaktivität,
  unbenutzbarem Passwort, leerer E-Mail und ohne Staff-/Superuser-Rechte
  weiterverwendet. Bei einer Kollision mit einem Webkonto entsteht ein
  getrenntes technisches Konto; ein unsicheres Konto im reservierten
  Namensraum führt zu `409 Conflict`. Webkonten werden dabei nicht geändert.
  Der Antrag wird bewusst **nicht** an ein
  bestehendes Web-Konto mit der E-Mail des Athleten gehängt: Das würde den
  Antrag samt Personendaten demjenigen zuordnen, der diese Adresse zuerst
  registriert hat. Die Kontaktdaten des Antragstellers stehen nur im Antrag.
- `created_via_api` und `api_key_prefix` werden am Antrag gespeichert.
- `external_reference` (Pflicht) macht wiederholte Requests idempotent und ist
  je API-Key durch einen Unique-Constraint in der Datenbank abgesichert; auch
  zwei gleichzeitige Retries erzeugen nur einen Antrag.
- `allowed_states`/`federal_access` begrenzen den gewählten Verband bzw. das
  gewählte Studio. Neue Starter- und internationale Anträge erfordern ein
  aktives Studio (`400` bei inaktivem Studio). Ein idempotenter Retry liefert
  den bestehenden Antrag auch nach späterer Deaktivierung des Studios.
- Technischer Benutzer, Antrag, ggf. neues Studio und der Mailversand laufen in
  **einer Transaktion**: Schlägt der Mailversand fehl, wird nichts gespeichert
  und die API antwortet `500`; der Client kann mit derselben
  `external_reference` erneut senden. Die Mails gehen nacheinander raus;
  scheitert der Versand mittendrin, haben die ersten Empfänger die Mail schon
  und bekommen sie beim Retry ein zweites Mal.
- Das Lizenz-PDF nach Bewilligung geht an die E-Mail-Adresse im Antrag (nicht
  an den technischen Benutzer). `pdf_sent` wird nur nach tatsächlichem Versand
  gesetzt. Ohne Empfänger bleibt es falsch; nach Ergänzen der Adresse kann
  der Versand erneut erfolgen. Änderungen an bereits versandten Anträgen
  lösen keinen weiteren automatischen PDF-Versand aus; erneute Bewilligung
  und der explizite Wiederholungsversand bleiben möglich.
- Studio-Anträge erzeugen wie der Webflow ein neues inaktives `Gym`.
- `send_emails()` wird wie im Webformular aufgerufen: Verwalter
  (`ManagerEmail`), Landesverband, ggf. Studio und Antragsteller bekommen die
  bekannte Mail, bei Zahlungsdaten mit einem zusätzlichen Zahlungsblock.
  Bei `payment.status = paid` entfällt die Überweisungsaufforderung.

### Formularoptionen

```
GET /api/v1/submissions/options/
```

Liefert nur die für den Key erlaubten Landesverbände und aktiven Studios,
außerdem Länder, Starter-Kategorien und die Zahlungsstatus-Werte.

### Starterantrag anlegen

```
POST /api/v1/submissions/starter/
Content-Type: application/json

{
  "gym": 10,
  "date_of_birth": "1990-05-01",
  "active_since": "2010",
  "last_name": "Mustermann",
  "first_name": "Max",
  "street": "Musterweg",
  "house_nr": "1",
  "zip_code": 12345,
  "city": "Koeln",
  "tel_number": "0123",
  "email": "max@example.org",
  "nationality": 37,
  "height": 180,
  "weight": "80.00",
  "category": "1",
  "terms_and_conditions": true,
  "data_protection": true,
  "submission_last_year": false,
  "external_reference": "NRW-ORDER-12345",
  "payment": {
    "status": "paid",
    "method": "nrw-website",
    "reference": "NRW-2026-12345",
    "amount_cents": 9000,
    "received_at": "2026-09-16T12:00:00+02:00",
    "note": "Bezahlt im NRW-Frontend"
  }
}
```

- Erfordert `allow_submit_starter`.
- `terms_and_conditions` und `data_protection` müssen ausdrücklich `true`
  sein; fehlende oder abgelehnte Bestätigungen ergeben `400`.
- `external_reference` ist Pflicht und je API-Key eindeutig. Wird dieselbe
  Referenz erneut gesendet, antwortet die API `200 OK` mit dem bestehenden
  Antrag und `reused: true`; eine Neuanlage antwortet `201 Created`.
- Der `payment`-Block erfordert `allow_register_payments`, sonst `403`.
  - `status`: `none`, `pending`, `paid`, `failed`, `refunded`.
  - `method`: Freitext, max. 40 Zeichen (z. B. Zahlungsanbieter des Frontends).
  - `reference`: max. 120 Zeichen; bei `paid` Pflicht.
  - `amount_cents`: bei `paid` Pflicht und **gleich der Gebühr** des
    Antragstyps (Starter 9000, Studio 3000, International und Kampfrichter
    2000), sonst `400`.
  - `received_at`: optional, darf nicht in der Zukunft liegen; fehlt es, wird
    der Eingangszeitpunkt des Requests gespeichert.
  - `note`: optional, max. 500 Zeichen.
- Ohne `payment`-Block bleibt der Antrag wie ein Webantrag ohne registrierte
  Zahlung (`payment_status = none`).

Antwort (`201`):

```json
{
  "id": 42,
  "license_type": "starter",
  "status": "Eingegangen",
  "payment_status": "Bezahlt",
  "bank_account_id": 2,
  "fee": 90,
  "designated_use": "Starterlizenz 42 Mustermann, Max",
  "external_reference": "NRW-ORDER-12345",
  "reused": false
}
```

`id` ist die Antragsnummer des Lizenzsystems; eine separate Lizenznummer gibt
es nicht. `designated_use` ist der Verwendungszweck für die Überweisung,
`bank_account_id` das zugehörige Konto des Verbands.

Die Endpunkte für `international`, `gym` und `judge` folgen demselben Muster mit
den jeweiligen Modellfeldern (siehe Swagger-UI) und eigenen Rechten.

## Lizenz-Endpoints (Kernfall NRW)

Eine „Lizenz" ist ein bewilligter Antrag für ein Kalenderjahr.
**Gültig = Status „Bewilligt" UND `creation_date.year == Jahr`** (Standard:
laufendes Jahr in `Europe/Berlin`, per `year` überschreibbar). Auch die
Validierung der Obergrenze „Folgejahr“ verwendet das Berliner Kalenderjahr.

### Gültigkeit gezielt abfragen (Lookup, datensparsam)

```
POST /api/v1/licenses/lookup/
Content-Type: application/json

{
  "last_name": "Mustermann",
  "date_of_birth": "1990-05-01",
  "year": 2026
}
```

Parameter: `last_name`, `first_name`, `email`, `date_of_birth` (`YYYY-MM-DD`),
`year` (optional, 2000 bis Folgejahr).

- Erfordert `allow_lookup_licenses`.
- Mindestens **zwei** Identifikatoren, davon mindestens einer **`email` oder
  `date_of_birth`**. Ein Namenspaar allein reicht nicht, weil es sich mit
  öffentlichen Namenslisten durchprobieren ließe. Sonst `400`.
- Die Felder werden exakt verglichen (Groß-/Kleinschreibung, keine
  Teilstrings).
- Die Identifikatoren werden ausschließlich im JSON-Body übertragen. `GET` ist
  deaktiviert, damit Namen, E-Mail-Adressen und Geburtsdaten nicht in URLs oder
  Access-Logs landen. Der POST ist semantisch read-only und benötigt kein
  `write_allowed`.
- Datenschutz: gibt **keine Personendaten** zurück, nur ob eine gültige Lizenz
  existiert (Typ + Jahr).
- Ein Typ wird nur geprüft, wenn er mindestens zwei der angegebenen Felder
  besitzt: Starter/International (alle vier), Kampfrichter (Name/E-Mail, kein
  Geburtsdatum). Studiolizenzen haben nur eine E-Mail und sind nur im
  Massen-Export enthalten.
- Bei Landesverbands-Keys werden nur Lizenzen der erlaubten Verbände geprüft.
  Mit `allow_lookup_all_states` prüft der Lookup bundesweit: Ein Athlet aus
  Hessen, der bei einem NRW-Wettkampf starten will, lässt sich so verifizieren,
  ohne dass NRW seine Daten sieht.

Antwort:

```json
{
  "year": 2026,
  "valid": true,
  "matches": [
    { "license_type": "starter", "label": "Starterlizenz", "year": 2026, "valid": true }
  ]
}
```

### Alle gültigen Lizenzen (Massen-Export)

```
GET /api/v1/licenses/valid/?year=2026&type=starter&page=1&page_size=100
```

- **Erfordert `sensitive_access` und `allow_export_licenses`**: es ist ein
  Personendaten-Export.
- `year` optional (Standard: laufendes Jahr, erlaubt 2000 bis Folgejahr),
  `type` optional: `starter` | `international` | `judge` | `studio`.
- Paginiert (`page`, `page_size`; Standard 100, Maximum 500), zählt und
  schneidet auf Datenbankebene. Eine Seite jenseits des Endes liefert leere
  `results`.
- Felder minimal. `date_of_birth` wird **nur** mit `?include=date_of_birth`
  mitgeliefert.
- Bei Landesverbands-Keys werden nur Lizenzen der erlaubten Verbände exportiert.

Antwort:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "license_type": "starter",
      "label": "Starterlizenz",
      "id": 42,
      "name": "Mustermann, Max",
      "year": 2026,
      "valid": true
    }
  ]
}
```

### Interaktive Doku / Schema

- Swagger-UI: `GET /api/v1/docs/`
- ReDoc: `GET /api/v1/redoc/`
- OpenAPI-Schema (JSON/YAML): `GET /api/v1/schema/`

Das Schema deklariert das Security-Scheme `ApiKeyAuth` global, generierte
Clients setzen den Header automatisch.

## Konfiguration

| Setting | Standard | Zweck |
|---|---|---|
| `DJANGO_SECURE` (Env) | aus | HTTPS-Härtung (Secure-Cookies, HSTS, SSL-Redirect, `X-Forwarded-Proto`) aktivieren, sobald TLS terminiert ist |
| `API_TRUSTED_PROXY_COUNT` | `0` | Anzahl vertrauenswürdiger Reverse-Proxies für die Client-IP |
| `API_PREAUTH_RATE_LIMIT` | `120/minute` | IP-Limit vor der Key-Prüfung |
| `API_KEY_REQUEST_RATE_LIMIT` | `5/hour` | Limit für das Beantragungsformular |
| `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['apikey']` | `1000/hour` | Limit pro Key |
| `CACHES` | Django-Default (LocMem) | Für Rate-Limits in Multi-Prozess-Deployments auf einen gemeinsamen Cache stellen |

### Betrieb / TLS

TLS wird von diesem Repository **nicht** bereitgestellt (die mitgelieferte
Apache-Konfiguration lauscht auf `:80`). HTTPS muss vom Reverse-Proxy des
Betreibers terminiert werden.

- Standard ist HTTP-tauglich (keine erzwungenen Secure-Cookies/Redirects).
- Sobald TLS sicher terminiert ist: `DJANGO_SECURE=1` setzen. Dann greifen
  Secure-Cookies, HSTS, SSL-Redirect und die Auswertung von `X-Forwarded-Proto`.
- Der Proxy muss eingehende `X-Forwarded-Proto`/`X-Forwarded-For`-Header
  überschreiben. Vor dem Aktivieren `python manage.py check --deploy` ausführen.

### Migrationen

- `api/0001`–`0009`: Key-Modell, Rechte-Flags, Zugriffsverlauf. `0003` und
  `0006` sind Datenmigrationen für Instanzen, auf denen die API bereits lief:
  bestehende Keys werden als Bundes-/System-Keys markiert bzw. bekommen die
  neu eingeführten Leserechte, damit laufende Integrationen nicht ausfallen.
  Auf einer Instanz ohne vorhandene Keys sind sie wirkungslos.
- `submission/0016`–`0018`: API-/Zahlungsfelder an allen Antragstypen;
  `external_reference` ist `NULL` für Webanträge und je API-Key eindeutig.

## Webhooks

Eine Änderungsbenachrichtigung per Webhook (Push an eine NRW-URL bei
Statuswechsel) ist **bewusst nicht Teil dieser API**: synchroner
Outbound-Versand, SSRF-Fläche und der Versand von Personendaten an Dritte
brauchen erst eine saubere Lösung (asynchrone Queue mit Retry, SSRF-Schutz,
DSGVO-Klärung). Kommt bei Bedarf in einem eigenen PR.

## Grenzen / offene Punkte

- Die Weboberfläche zeigt API-Herkunft und Zahlungsvermerk eines Antrags noch
  nicht an; beides steht in der Datenbank, im generischen Read-Endpunkt und in
  der Benachrichtigungsmail.
- Bei Key-Rotation (neuer Prefix) gelten alte `external_reference`-Werte als
  neu; Referenzen sind je Key eindeutig. Vor der Rotation offene Bestellungen
  abschließen.
- `APIAccessLog` wächst unbegrenzt; eine Aufbewahrungsfrist ist Betreibersache.
- Die Gebühren (`FEE`) sind Konstanten am Modell; die Betragsprüfung der
  Zahlungsregistrierung folgt ihnen.
