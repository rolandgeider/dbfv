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

from django.core import mail
from django.conf import settings

from django.core.management.base import BaseCommand
from core.models import EmailCron


class Command(BaseCommand):
    '''
    Sends the prepared mass emails
    '''

    def handle(self, *args, **options):
        '''
        Send some mails and remove them from the list
        '''
        if EmailCron.objects.count():
            for email in EmailCron.objects.all()[:100]:
                mail.send_mail(email.subject,
                               email.body,
                               settings.DEFAULT_FROM_EMAIL,
                               [email.email],
                               fail_silently=True)
                email.delete()
