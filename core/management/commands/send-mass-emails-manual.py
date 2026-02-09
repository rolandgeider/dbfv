# -*- coding: utf-8 *-*
import datetime
# This file is part of the DBFV submission site
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import os
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

# Django
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from submission.models import Gym, SubmissionStarter


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
        this_year = datetime.date.today().year
        status = SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT
        # for submission in SubmissionStarter.objects.filter(creation_date__year=this_year,
        #                                                    submission_status=status):
        #     if submission.email:
        #         email_list.append(submission.email)

        ### Gyms
        for gym in Gym.objects.filter(is_active=True):
           if gym.email:
                email_list.append(gym.email)
        #print(email_list)

        # Debug mode
        #email_list = []
        #email_list.append('falkeohnee@aol.com')
        #email_list.append('roland@geider.net')
        # email_list.append('koenig@dbfv.de')
        #email_list.append('schrecksenmeister.eisspin@gmail.com')
        #print(email_list)

        email_images = [
            'image1.png',
        ]
        email_images = []
        #email_files_others = ['Infos_Homepage.pdf', ]
        email_files_others = []
        email_from = 'no-reply@dbfv.de'
        email_subject = 'Newsletter - Black Week'
        email_text = u'Textversion nicht verfügbar, bitte öffnen Sie die HTML Variante'
        email_html = u"""
            <p>Hallihallo! :)</p>
            <p>Wir freuen uns von euch zu hören,,<br>
                euer nutriful Team
            </p>
            <img src="cid:DE_Fitness_Markt_Black_Week_Fitness_Club_24 (1).png" style="width:100%;">
            """
        email_html = """
<p>Liebe Mitglieder,</p>
 
<p>
    Schaut euch das Spezialangebot für DBFV-Mitglieder an:
    <a href="https://drive.google.com/open?id=1nC9wFW_VrFCVFcpYjPncw9WS2ZDI8J5y&authuser=forall.fc24%40gmail.com&usp=drive_fs">Black Week Angebote</a>
</p>
 
 
<p>
📲 <a href="tel:+48334869007">+48 33 486 90 07</a><br>
📧 <a href="mailto:sklep@fitnessclub24.pl">sklep@fitnessclub24.pl</a><br>
 
👉 <a href="https://www.fitnessclub-24.de">https://www.fitnessclub-24.de</a><br>
🛒 <a href="https://bit.ly/FitnessMarkt_FC24">https://bit.ly/FitnessMarkt_FC24</a><br>
</p>

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
