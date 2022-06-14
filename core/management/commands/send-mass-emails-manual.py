# -*- coding: utf-8 *-*

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText
# from email.MIMEImage import MIMEImage

# Standard Library
import os
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

# Django
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Sends the prepared mass emails
    """

    def handle(self, *args, **options):
        """
        Send emails with inline images, manual steps needed
        """
        email_list = []

        ### Submissions
        # this_year = datetime.date.today().year
        # status = SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT
        # for submission in SubmissionStarter.objects.filter(creation_date__year=this_year,
        #                                                    submission_status=status):
        #     if submission.email:
        #         email_list.append(submission.email)

        ### Gyms
        #for gym in Gym.objects.filter(is_active=True):
        #    if gym.email:
        #        email_list.append(gym.email)
        #print(email_list)

        # Debug mode
        email_list = []
        email_list.append('falkeohnee@aol.com')
        email_list.append('roland@geider.net')
        email_list.append('schrecksenmeister.eisspin@gmail.com')
        #print(email_list)

        email_images = [
            'image1.jpg',
        ]
        #email_images = []
        #email_files_others = ['Infos_Homepage.pdf', ]
        email_files_others = []
        email_from = 'no-reply@dbfv.de'
        email_subject = 'Newsletter'
        email_text = u'Textversion nicht verfügbar, bitte öffnen Sie die HTML Variante'
        ##email_text = """
        ##    In Zusammenarbeit mit XXL Nutrition können wir unseren Mitgliedern
        ##    einen 10% Rabattcode anbieten. XXL Nutrition hat ein sehr breites
        ##    Sortiment an Ergänzungen von verschiedenen Marken.

        ##    Rabattcode: DBFV10

        ##    Diesen Code könnt ihr im Warenkorb eingeben bevor ihr Zahlt, er ist
        ##    bis 4 juli 2016 gültig.

        ##    Profitiert jetzt sofort beim XXL Nutrition Shop
        ##    https://xxlnutrition.com/de/deu
        ##    """
        email_html = u"""
            <p>Hallihallo! :)</p>

<p>
    Mit dieser Mail wollten wir euch die Mitte der Arbeitswoche versüßen und
    euch auf ein paar Aktionen aufmerksam machen, von denen ihr sicherlich
    super profitieren könnt!
</p>
<ul>
    <li>
        Alle Saucen und Flavor Drops im alten Design sind nun dauerhaft reduziert.
        So bekommt ihr die <strong>Saucen</strong> zu einem Preis von
        <strong>1,49€-1,99€</strong> pro Flasche und die <strong>Flavor Drops</strong>
        für nur <strong>2,49€</strong> pro Flasche. Dabei <strong>spart ihr
        zwischen 45% und 63%</strong> auf den eigentlichen Preis! :)
    </li>
    <li>
        Der BodyAdvice Shop wird geschlossen. Daher werden alle Produkte zum EK
        verkauft. Gerade das <strong>Straight Whey</strong> hat ein super Preis-Leistungs-Verhältnis
        und ist in 10 Geschmacksrichtungen für <strong>9,99€ pro 1kg</strong> zu haben!
    </li>
</ul>

<p>
    Falls es jemand beim letzten Mal verpasst hat: Wir finden eure Leistungen bemerkenswert und möchten daher jeden Einzelnen von euch gerne unterstützen!
</p>

<p>
    <strong>Ihr sollt nicht nur als Erstes von neuen Produkten erfahren und diese
    testen können, sondern werdet ab sofort mit 15% Rabatt auf alle Produkte in
    unserem Shop gesponsert*!</strong> Durch einen gesonderten Zugang zu unserem
    Shop werden euch die Produkte direkt rabattiert angezeigt, sobald ihr
    eingeloggt seid (*ausgenommen Sale-Artikel).
</p>

<p>
    Was ihr dafür tun müsst?
</p>

<ol>
    <li>Registiert euch als Kunde auf <a href="https://shop.nutriful.eu/registrieren.php">https://shop.nutriful.eu/registrieren.php</li>
    <li>
        Schickt uns eine Mail an <a href="mailto:kathy@nutriful.eu">kathy@nutriful.eu</a>
        mit eurer Starterlizenz-Nummer,
        damit wir euch der Athletengruppe zuordnen können.</li>
    <li>Sobald ihr freigeschalte seid, erhaltet ihr eine Mail von uns.</li>
    <li>Einloggen, drauf los shoppen und die Diät rocken!</li>
</ol>

<p>
    Wir freuen uns von euch zu hören,,<br>
euer nutriful Team
</p>



            <img src="cid:image1.jpg" style="width:100%;">
            """
        email_html = """
<p>Wir haben eine Kooperation mit dem DBFV e.V. geschlossen!</p>
<p>Jedes assoziierte Mitglied erhält ein spezielles Angebot mit Regenerierten Fitnessgeräten von uns!</p>
<p>Außerdem haben wir für Sie ein Sonderangebot für neue Fitnessgeräte -40%.</p>

<p>Verwenden Sie den Code #DBFV, wenn Sie mit uns Kontakt aufnehmen.</p>

<p>über uns:</p>
<ul>
    <li>Wir sind einer der größten Spieler  auf dem Markt für überholte Geräte.</li>
    <li>Bei uns finden Sie alle Marken, nach denen Sie gesucht haben: Life Fitness, TechnoGym, Gym80, Matrix, Precor, Cybex, Hammerkraft, Freemotion, Star Track...</li>
    <li>Wir beraten Sie über die Art der Finanzierung, Transport, Montage, Service, Hilfe bei den Formalitäten.</li>
    <li>Wir statten Ihren Club auch mit Schließfächern, Rezeption, Beleuchtung aus... von A bis Z.</li>
    <li>Wir haben neue, überholte und gebrauchte Geräte.</li>
</ul>
 
<p>Sehen Sie, wie wir arbeiten: <a href="https://youtu.be/f2LJ7QOg4Q4">https://youtu.be/f2LJ7QOg4Q4</a></p>


 
<p>Kontaktieren Sie uns:</p>


<p>
📲 +48 33 486 90 07<br>
📧 sklep@fitnessclub24.pl<br>
👉 https://www.fitnessclub-24.de<br>
Marketing: <a href="https://www.fitnessclub24.pl/info">https://www.fitnessclub24.pl/info</a>
</p>

<img src="cid:image1.jpg" style="width:100%;">
"""
        ##<img src="cid:image1.jpg">

        # Process and send all emails
        counter = 1
        for email_recipient in email_list:
            print(
                'Sending mail {0} from {1} ({2})'.format(counter, len(email_list), email_recipient)
            )
            msg = EmailMultiAlternatives(email_subject, email_text, email_from, [email_recipient])
            msg.attach_alternative(email_html, "text/html")
            msg.mixed_subtype = 'related'
            for image_file in email_images:
                fp = open(os.path.join(os.path.dirname(__file__), image_file), 'rb')
                msg_img = MIMEImage(fp.read())
                fp.close()
                msg_img.add_header('Content-ID', '<{}>'.format(image_file))
                msg.attach(msg_img)

            for other_file in email_files_others:
                fp = open(os.path.join(os.path.dirname(__file__), other_file), 'rb')
                msg_part = MIMEApplication(fp.read())
                fp.close()
                msg_part['Content-Disposition'] = 'attachment; filename="{}"'.format(other_file)
                msg.attach(msg_part)

            counter += 1
            msg.send()
