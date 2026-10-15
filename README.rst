Antragssystem des DBFV e.V.
===========================

Das ist der Quellcode des Antragssystems des DBFV e.V. zur Verwaltung von
Starter-, Studio- und Kampfrichterlizenzen. Es kann momentan unter
http://dbfv.rge.vela.uberspace.de/ erreicht werden.


Installation
============

Diese Installationsschritte gehen von einem Linux-System aus. Das Antragssystem
ist eine Djangoanwendung, schaue dir die offizielle Dokumentation an wenn etwas
nicht funktioniert oder du ein anderes Setup hast: http://djangoproject.com/


1) Virtualenv für python erstellen, nötige Pakete und Abhängigkeiten
   runterladen.

::

 $ sudo apt-get install python-virtualenv
 $ sudo apt-get install python-dev
 $ virtualenv python-django
 $ source python-django/bin/activate
 $ git clone https://github.com/rolandgeider/dbfv.git
 $ cd dbfv
 $ uv sync            # oder: pip install .
 $ cd submission/static
 $ yarn install

2) Quellcode runterladen und settings-Datei sowie Datenbank erstellen:

::

 $ cp dbfv/settings_sample.py dbfv/settings.py
 $ vim dbfv/settings.py
 $ python manage.py migrate


3) Fixtures laden und Anwendung starten

::

 $ python manage.py createsuperuser
 $ python manage.py loaddata groups bank_accounts federal_states countries gyms
 $ python manage.py runserver


REST-API
========

Unter ``/api/v1/`` gibt es eine REST-API mit API-Key-Authentifizierung, mit
der berechtigte Landesverbände Lizenzgültigkeiten abfragen und Anträge samt
Zahlungsvermerk anlegen können. API-Keys werden im Django-Admin
(``/admin/``, Bereich „API-Keys“) ausgestellt; jeder Key ist auf einzelne
Landesverbände und einzelne Rechte beschränkbar. Interaktive Doku unter
``/api/v1/docs/``.

* Technische Dokumentation: ``API.md``
* Erklärung für Verband und Geschäftsstelle: ``API-README.md``
* Änderungen: ``CHANGELOG.md``




Quellcode
=========

Der Quellcode kann von Github heruntergeladen werden:

* https://github.com/rolandgeider/dbfv


Lizenz
======

Die Anwendung ist unter der Affero GNU General Public License 3 oder später
(AGPL 3+) verfügbar und darf ohne Restriktionen (unter den Bedingungen der Lizenz)
benutzt, verändert und (geändert) weitergegeben werden. Siehe die AGPL.txt-Datei
für weitere Einzelheiten.
