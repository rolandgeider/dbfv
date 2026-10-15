# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden hier dokumentiert.

Format angelehnt an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

Bündelt die REST-API (vormals PR #157), das UI-Redesign (vormals PR #158) und
die darauf aufbauende Landesverbands-API für Antrags- und Zahlungsflow.
Entwickelt im Auftrag des DBFV NRW.

### Hinzugefügt – REST-API

- REST-API unter `/api/v1/` auf Basis von Django REST Framework, inklusive
  OpenAPI-Schema (`/api/v1/schema/`), Swagger-UI (`/api/v1/docs/`) und ReDoc
  (`/api/v1/redoc/`) via drf-spectacular. Django-Admin unter `/admin/`
  aktiviert (war zuvor nicht eingebunden).
- API-Key-Authentifizierung (`djangorestframework-api-key`) mit eigenem
  Key-Modell `ScopedAPIKey`; jedes Recht ist ein eigenes Flag:
  - `allowed_states` – Landesverbandsgrenze; der Key sieht und schreibt nur
    Daten der gewählten Verbände.
  - `federal_access` – expliziter Bundes-/Systemzugriff über alle Verbände;
    nur damit sind Bankkonten, Manager-E-Mails und Mail-Cron erreichbar.
  - `allow_lookup_licenses`, `allow_export_licenses`, `allow_read_submissions`
    – Leserechte für Lizenz-Lookup, Lizenz-Export und Roh-Anträge;
    `allow_lookup_all_states` lässt den Lookup bundesweit prüfen (Gaststarter
    anderer Landesverbände), weiterhin ohne Personendaten in der Antwort.
  - `allow_submit_starter`, `allow_submit_international`, `allow_submit_gym`,
    `allow_submit_judge`, `allow_register_payments` – fachliche Antragsanlage
    und Zahlungsregistrierung.
  - `sensitive_access` – personen-/finanzbezogene Ressourcen.
  - `write_allowed` – generisches Schreiben; `DELETE` zusätzlich nur mit
    `sensitive_access`.
  - `allowed_ips` – optionale IP-/CIDR-Allowlist.
- Generische Endpunkte: CRUD für Stammdaten und Profile (Gym, State, Country,
  UserProfile; BankAccount, ManagerEmail, EmailCron nur mit Bundeszugriff),
  read-only Listen/Details für Submission*, jeweils mit Filter (`?feld=wert`),
  Suche (`?search=`), Sortierung (`?ordering=`) und Pagination.
- Lizenz-Endpoints („gültig" = Status Bewilligt im Kalenderjahr nach
  `Europe/Berlin`, auch in der Neujahrsstunde; `year` 2000 bis Folgejahr):
  - `POST /api/v1/licenses/lookup/` – datensparsame Gültigkeitsabfrage:
    mindestens zwei Identifikatoren, davon einer E-Mail oder Geburtsdatum;
    Rückgabe nur Typ/Jahr/gültig, keine Personendaten.
  - `GET /api/v1/licenses/valid/` – Massen-Export mit `sensitive_access` und
    `allow_export_licenses`; DB-seitig paginiert (max. 500), minimale Felder,
    `date_of_birth` nur mit `?include=date_of_birth`.
- Fach-Endpunkte für Landesverbände:
  - `GET /api/v1/capabilities/` – Rechte und erlaubte Verbände des Keys.
  - `GET /api/v1/submissions/options/` – verbandsspezifische Formularoptionen.
  - `POST /api/v1/submissions/{starter,international,gym,judge}/` – legen
    Anträge über den Fachworkflow an (technischer Benutzer je Key, Verbandsgrenze,
    Zahlungsvermerk, bestehender Mailversand an Verwalter, Landesverband,
    Studio und Antragsteller; Studio-Anträge erzeugen ein inaktives `Gym`).
    Idempotent über `external_reference` (je Key eindeutig, DB-Constraint):
    Wiederholung liefert `200` mit `reused: true` statt eines Doppelantrags,
    auch wenn das Studio inzwischen deaktiviert wurde. Neue Starter- und
    internationale Anträge brauchen ein aktives Studio, Regeln und Datenschutz
    müssen ausdrücklich bestätigt sein. Antrag, Studio und Mails laufen in
    einer Transaktion.
- Zahlungsfelder an allen Antragstypen (`created_via_api`, `api_key_prefix`,
  `external_reference`, `payment_status`, `payment_method`,
  `payment_reference`, `payment_amount_cents`, `payment_received_at`,
  `payment_note`). Bei `status = paid` sind Referenz und ein Betrag in Höhe der
  Gebühr Pflicht; Zahlungszeitpunkt nicht in der Zukunft, Notiz max. 500
  Zeichen. Die Benachrichtigungsmails enthalten einen Zahlungsblock; bei
  `paid` entfällt die Überweisungsaufforderung. Die Kontozuordnung je
  Landesverband (`get_bank_account()`, Sonderfälle NRW/Berlin) bleibt
  unverändert; Zahlungsregistrierung ist pro Key abschaltbar (Standard aus).
- Öffentliches Formular „API-Key beantragen" (`/api-key/anfrage`, Footer-Link)
  mit Honeypot; Anfragen gehen per E-Mail an die Manager-Adressen.
- `API.md` (technische Doku), `API-README.md` (Erklärung für Verband und
  Geschäftsstelle), API-Abschnitt in `README.rst`.

### Sicherheit

- Landesverbandsgrenze serverseitig: gescopte Keys sehen Listen/Details nur
  des eigenen Verbands (fremde Details `404`), Schreibversuche auf fremde
  Daten `403`. Bundesweite Ressourcen (Bankkonto – von mehreren Verbänden
  geteilt –, Manager-E-Mails, Mail-Cron) sind für gescopte Keys unsichtbar und
  unveränderbar; Bundesländer können gescopte Keys weder ändern noch löschen.
- API-Anträge hängen an einem technischen Benutzer je API-Key im nicht
  registrierbaren Namensraum `api:<hex-PREFIX>` (inaktiv, ohne Passwort und
  E-Mail) und werden nie an bestehende Web-Konten gebunden; ein fremdes Konto
  im reservierten Namensraum führt zu `409`. Das Lizenz-PDF nach Bewilligung
  geht an die Adresse im Antrag (`pdf_recipient()`), nicht an den
  Kontoinhaber; `pdf_sent` folgt dem tatsächlichen Versanderfolg, ohne
  Empfänger wird kein Versand vorgetäuscht, eine unveränderte Bewilligung löst
  kein zweites PDF aus.
- Web-Anlage von Antrag und ggf. Studio läuft in einer Transaktion und wird
  bei Mailfehlern zurückgerollt (keine verwaisten oder doppelten Datensätze).
- Länder und Benutzerprofile sind für gescopte Keys read-only (kein Hochstufen
  auf Bundesverband, kein Verschieben aus dem Verband); `year` ist im Export
  wie im Lookup auf 2000 bis Folgejahr begrenzt (vorher `500` bei Unsinn).
- Rate-Limiting pro API-Key (1000/Stunde) plus vorgelagertes IP-Limit vor der
  Key-Prüfung (`API_PREAUTH_RATE_LIMIT`, 120/Minute); Beantragungsformular
  zusätzlich pro IP (`API_KEY_REQUEST_RATE_LIMIT`).
- Client-IP-Ermittlung: `X-Forwarded-For` wird standardmäßig ignoriert
  (`API_TRUSTED_PROXY_COUNT = 0`), Proxy-Betrieb nur explizit, fail-closed.
- Audit-Logging (`dbfv.audit`) und Admin-einsehbarer Zugriffsverlauf
  (`APIAccessLog`): Zeit, Key-Prefix (max. 8 Zeichen), IP, Methode, Pfad ohne
  Query, Status; `401`/`403`/`429` und Key-Widerrufe als Warnung. Ohne
  Key-Secret, Body, Zahlungsdaten oder Suchparameter.
- Produktions-Settings sicher als Standard: `DEBUG=False`, `X-Frame-Options:
  DENY`, `SECURE_CONTENT_TYPE_NOSNIFF`; HTTPS-Härtung als Opt-in über
  `DJANGO_SECURE=1`, `X-Forwarded-Proto` nur dann ausgewertet.
  `SecurityMiddleware` eingebunden, ohne die die `SECURE_*`-Settings keine
  Wirkung hätten (`check --deploy`, W001).
- OpenAPI-Security-Scheme `ApiKeyAuth` global deklariert; Envelope-Serializer
  für Lookup und Export, damit Schema und Antworten übereinstimmen.
- Altlasten unabhängig von der API: IDOR bei Kampfrichteranträgen behoben
  (Owner-/Rechteprüfung in der Detail-View); Rechteprüfung in gemeinsamen
  Submission-Views aus dem konkreten Modell abgeleitet; CSV-/TSV-Exporte gegen
  Spreadsheet-Formula-Injection neutralisiert; „PDF erneut senden" nur per POST
  mit CSRF; Haupt-Mails bei Antragsanlage nicht mehr stillschweigend verworfen
  (`fail_silently=False`); Kampfrichterantrag ohne E-Mail-Adresse ließ den
  Mailversand mit `None` als Empfänger scheitern (`SubmissionJudge.get_email_list`).

### Hinzugefügt – Antragsseiten Design 2.0

- Mehrstufige Antragsformulare (Wizard) für Starter- und Internationale
  Anträge: Studio → Persönliches → Wettkampf → Bestätigung (International mit
  vorgeschaltetem Schritt „Voraussetzungen"). Der Antrag wird weiterhin in
  einem POST abgeschickt; Schritte sind rein clientseitig, serverseitige
  Validierung unverändert (`submission/templates/tags/wizard.html`,
  `submission/forms.py`, `starter/create.html`, `international/create.html`).
- Neue Studioauswahl `submission/templates/tags/studio_picker.html`: Suche
  nach Name/Ort, optionaler Bundesland-Filter mit Anzahl, Studios als
  anklickbare Karten (Radios, barrierefrei); natives `gym`-Feld als
  noscript-Fallback.
- Rechtstexte (Regeln, Anti-Doping, DSGVO) im Modal mit Scroll-Gate; die
  Zustimmungs-Checkboxen werden erst nach vollständigem Lesen aktiv.
- Design-Layer in `submission/templates/base.html`: Design-Tokens, neue
  Navbar, Cards, Sticky-Footer, Seitentitel, `lang="de"`, Favicon;
  Startseite als Karten-Grid (`index.html`); Detail- und Listenseiten mit
  Status-Badges; Bootstrap-3-Reste ersetzt; Textkorrekturen.
- Feldtypen für Client-Validierung je Wizard-Schritt (`date`, `tel`,
  numerische `inputmode`/`min`/`max`/`step`) in `submission/forms.py`.
- Wizard-Nachbesserungen nach Review: sichtbare Fehlermeldung, wenn ohne
  Studio auf „Weiter" geklickt wird (das native Select ist versteckt, die
  Browser-Blase konnte nicht erscheinen); Hinweis statt stummem Server-Roundtrip,
  wenn die Zustimmung noch hinter dem Scroll-Gate liegt; Doppelklick-Schutz
  beim Absenden; `aria-current="step"` und Fokus auf den Schritttitel.
  Die Voraussetzungs-Bestätigung des internationalen Antrags ist jetzt ein
  echtes Formfeld (`requirements_ack`), per `form=` auch ohne JavaScript dem
  Formular zugeordnet und serverseitig geprüft. Alle Absendewege (Button,
  Enter) validieren sämtliche Schritte; ohne JavaScript bleiben alle Schritte
  sichtbar (`.wizard.is-enhanced`). Die Bearbeitungsseiten beider Anträge
  nutzen denselben Wizard samt Studioauswahl.
- Design-Layer aus `base.html` nach `submission/static/css/dbfv.css`
  ausgelagert (Tokens durchgängig, kein hartes Rot mehr, Studio-Picker-Styles
  dabei). Zahlungsblock der Benachrichtigungsmails als Include
  `tags/email_payment_block.html`, Betrag als „90,00 €". Library-Admin für das
  ungenutzte Basis-`APIKey`-Modell ausgeblendet. Kleinkram: Sie-Form im
  API-Key-Formular, BS3-Reste (`alert-error`, `data-toggle`), `rel="noopener"`,
  einheitliche Währungsschreibweise, falsche `title`-Attribute, Kampfrichter-PDF
  hieß `Starterlizenz-<id>.pdf`.

### Geänderte Dateien

- Neu: `api/` (App: `access.py`, `admin.py`, `apps.py`, `audit.py`,
  `client_ip.py`, `contact.py`, `licenses.py`, `middleware.py`, `models.py`,
  `permissions.py`, `rate_limit.py`, `submissions.py`, `tests.py`,
  `test_license_year.py`, `throttling.py`, `urls.py`, `views.py`,
  `migrations/0001`–`0009`,
  `templates/api/api_key_request.html`, `templates/api/api_key_request_email.txt`),
  `API.md`, `API-README.md`, `CHANGELOG.md`, `.python-version` (3.13: Django
  5.1 läuft nicht auf 3.14), `submission/migrations/0016`–`0018`,
  `submission/templates/tags/studio_picker.html`,
  `submission/templates/tags/wizard.html`,
  `submission/templates/tags/email_payment_block.html`,
  `submission/static/css/dbfv.css`, `submission/test_forms.py`,
  `submission/test_lifecycle.py`.
- Geändert: `.gitignore` (`*.sqlite3`, `.venv/`, `.DS_Store`), `README.rst`,
  `pyproject.toml`/`uv.lock` (DRF, api-key, django-filter, drf-spectacular),
  `dbfv/settings_global.py` (Apps, DRF/Spectacular-Settings, Middleware,
  Security-Defaults, Audit-Logger, `API_*`-Settings), `dbfv/urls.py`
  (`/api/v1/`, `/admin/`, `/api-key/anfrage`), `submission/models.py`
  (API-/Zahlungsfelder, Unique-Constraint, `fail_silently=False`),
  `submission/forms.py`, `submission/views/generic_views.py`,
  `submission/views/gym.py`, `submission/views/submission_judge.py`,
  `submission/views/submissions.py`,
  `submission/views/submissions_international.py`, Templates `base.html`, `delete.html`,
  `index.html`, `user/login.html`, `tags/render_form_submit.html`,
  `tags/render_submission_list.html`, `submission/{starter,international}/create.html`,
  `submission/{starter,international,judge}/list.html`,
  `submission/{starter,judge}/view.html`,
  `submission/{starter,international,gym,judge}/email_new_submission.html`
  (Zahlungsblock).
