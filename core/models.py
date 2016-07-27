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

import os

from django.conf import settings
from django.template.loader import render_to_string
from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core import mail


class EmailCron(models.Model):
    '''
    List of emails to be sent bit by bit by a cron job
    '''

    subject = models.CharField(max_length=100)
    '''
    The email subject
    '''

    body = models.TextField()
    '''
    The email's body
    '''

    email = models.EmailField()
    '''
    The email address
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.email
