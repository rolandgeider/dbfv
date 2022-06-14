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

import csv
import datetime
import logging
from email.mime.application import MIMEApplication

from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.http import HttpRequest, HttpResponse

from submission.helpers import build_submission_pdf
from submission.models import Gym, SubmissionStarter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Send an email to submissions
    """

    def handle(self, *args, **options):
        """
        Process the options
        """

        email_subject = 'Titel der Email'
        email_text = """Sehr geehrte Damen und Herren,

...
"""

        for submission in SubmissionStarter.objects.filter(
            pdf_sent=False, submission_status=SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT
        ):

            logger.warning(
                f'Sending PDF for submission {submission.id} - ({submission.user.email})'
            )
            msg = EmailMultiAlternatives(
                email_subject, email_text, settings.DEFAULT_FROM_EMAIL, [submission.user.email]
            )
            msg.mixed_subtype = 'related'

            # Build the PDF and attach it to the email
            response = HttpResponse(content_type='application/pdf')
            build_submission_pdf(HttpRequest(), submission.pk, response)
            msg_part = MIMEApplication(response.content)
            msg_part['Content-Disposition'
                     ] = f'attachment; filename="Starterlizenz-{submission.id}.pdf"'
            msg.attach(msg_part)

            # Send the email
            msg.send()

            # Flag the submission as sent
            #submission.pdf_sent = True
            #submission.save()
