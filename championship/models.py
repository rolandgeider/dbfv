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

from django.db import models
from django.utils import formats
from submission.models import State


class Championship(models.Model):
    '''
    Championship used in
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["date", "name"]

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

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u'{0} ({1})'.format(self.name, formats.date_format(self.date, "SHORT_DATE_FORMAT"))


class Category(models.Model):
    '''
    Category in a Championship
    '''
    class Meta:
        '''
        Configure other properties
        '''
        ordering = ["name"]

    championship = models.ForeignKey(Championship,
                                     verbose_name='Meistershaft',
                                     editable=False)
    '''
    Championship this category belongs to
    '''

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
