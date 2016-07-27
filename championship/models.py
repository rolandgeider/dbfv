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

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import formats
from submission.models import State, SubmissionStarter

championship_fields = ('name', 'date', 'state', 'categories')
judge_fields = ('name', )
placement_fields = ('category', 'placement')


class Championship(models.Model):
    '''
    A Championship
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["-date", "name"]

    name = models.CharField(verbose_name='Name',
                            max_length=50)
    '''
    The championship's name
    '''

    date = models.DateField(verbose_name='Datum')
    '''
    The championship's date
    '''

    state = models.ForeignKey(State,
                              verbose_name='Bundesland')
    '''
    The federal state the championship happens in
    '''

    categories = models.ManyToManyField('Category',
                                        verbose_name='Kategorien')
    '''
    All available categories for this championship
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'{0} ({1})'.format(self.name, formats.date_format(self.date, "SHORT_DATE_FORMAT"))

    @property
    def total_participants(self):
        '''
        Returns the total number of participants
        '''
        return self.participation_set.count()


class Category(models.Model):
    '''
    Category in a Championship
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["name"]

    name = models.CharField(verbose_name='Name',
                            max_length=50)
    '''
    The category's name
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'{0}'.format(self.name)


class Judge(models.Model):
    '''
    A Judge in a Championship
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["name"]

    name = models.CharField(verbose_name='Name',
                            max_length=50)
    '''
    The judge's name
    '''

    championship = models.ForeignKey(Championship,
                                     editable=False)
    '''
    The championship
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'{0}'.format(self.name)


def limit_championship_choices():
    return {'date__gte': datetime.date.today()}


class Participation(models.Model):
    '''
    Intermediate table for championship participation
    '''

    class Meta:
        '''
        Configure other properties
        '''
        unique_together = (("championship", "participation_nr"),
                           ("championship", "submission"))

    submission = models.ForeignKey(SubmissionStarter,
                                   editable=False,
                                   verbose_name='Antrag')
    '''
    The user participating in a championship
    '''

    participation_nr = models.IntegerField(editable=False,
                                           verbose_name='Teilnehmernummer')
    '''
    A unique identification number per user and championship
    '''

    championship = models.ForeignKey(Championship,
                                     limit_choices_to=limit_championship_choices,
                                     verbose_name='Meisterschaft')
    '''
    The championship
    '''

    def get_absolute_url(self):
        '''
        Return the detail view URL
        '''
        return reverse('championship:participation:view', kwargs={'pk': self.pk})


class Placement(models.Model):
    '''
    A placement for an athlete in a championship for a specific category
    '''

    class Meta:
        '''
        Configure other properties
        '''
        unique_together = (("participation", "category"))

    participation = models.ForeignKey(Participation,
                                      editable=False,
                                      verbose_name='Teilnahme')
    '''
    The participation (basically, a championship) for this placement
    '''

    category = models.ForeignKey(Category,
                                 verbose_name='Kategorie')
    '''
    The categories in the championship
    '''

    placement = models.IntegerField(default=0,
                                    verbose_name='Platzierung')
    '''
    The user's placement in this championship and category
    '''
