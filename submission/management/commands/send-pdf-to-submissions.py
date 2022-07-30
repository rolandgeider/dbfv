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

# Standard Library
import logging
from email.mime.application import MIMEApplication

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.http import (
    HttpRequest,
    HttpResponse,
)

# dbfv
from submission.models import SubmissionStarter


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Send an email to submissions
    """

    def handle(self, *args, **options):
        """
        Process the options
        """

        for submission in SubmissionStarter.objects.filter(
            pdf_sent=False, submission_status=SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT
        ):
            # Send the PDF for the submission
            submission.send_pdf_email()

            # Flag it as sent
            submission.pdf_sent = True
            submission.save()
