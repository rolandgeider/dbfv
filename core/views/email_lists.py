# -*- coding: utf-8 -*-

# This file is part of the DBFV site.
#
# the DBFV site is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# the DBFV site is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with the DBFV site.  If not, see <http://www.gnu.org/licenses/>.

import datetime

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core import mail
from django.urls import reverse
#from formtools.preview import FormPreview

from core.models import EmailCron
from submission.models import ManagerEmail, SubmissionStarter, Gym


class EmailListFormPreview():  #FormPreview
    preview_template = 'email/preview.html'
    form_template = 'email/form.html'
    list_type = None

    def parse_params(self, *args, **kwargs):
        """
        Save the current recipient type
        """
        self.list_type = kwargs['type']

    def get_context(self, request, form):
        """
        Context for template rendering.
        """
        context = super(EmailListFormPreview, self).get_context(request, form)
        context['form_action'] = reverse('core:email:add', kwargs={'type': self.list_type})
        context['email_type'] = self.list_type

        return context

    def process_preview(self, request, form, context):
        """
        Send an email to the managers with the current content
        """
        for email in ManagerEmail.objects.all():
            mail.send_mail(
                form.cleaned_data['subject'],
                form.cleaned_data['body'],
                settings.DEFAULT_FROM_EMAIL, [email.email],
                fail_silently=False
            )
        return context

    def done(self, request, cleaned_data):
        """
        Collect appropriate emails and save to database to send for later
        """
        email_list = []

        # Select all successful starter submissions for the current year
        if self.list_type == 'starter':
            this_year = datetime.date.today().year
            status = SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT
            for submission in SubmissionStarter.objects.filter(
                creation_date__year=this_year, submission_status=status
            ):
                if submission.email:
                    email_list.append(submission.email)

        # Select all active gyms
        else:
            for gym in Gym.objects.filter(is_active=True):
                if gym.email:
                    email_list.append(gym.email)

        # Make unique, so people don't get duplicate emails later
        email_list = list(set(email_list))

        # Save entries to list to be processed later
        for email in email_list:
            cron = EmailCron()
            cron.email = email
            cron.subject = cleaned_data['subject']
            cron.body = cleaned_data['body']
            cron.save()

        return HttpResponseRedirect('/')
