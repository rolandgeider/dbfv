# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class State(models.Model):
    '''
    Model for a state
    '''

    name = models.CharField(verbose_name=_('Name'),
                            max_length=100,)
    short_name = models.CharField(verbose_name=_('Short name'),
                                  max_length=2,)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name


class Gym(models.Model):
    '''
    Model for a gym
    '''

    name = models.CharField(verbose_name=_('Name'),
                            max_length=100,)
    email = models.EmailField(verbose_name=_('Email'))
    state = models.ForeignKey(State, verbose_name=_('State'))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name


class StateAssociation(models.Model):
    '''
    Model for a State Association (Landesverband)
    '''

    state = models.ForeignKey(State, verbose_name=_('State'))
    bank_account = models.CharField(verbose_name=_('Name'),
                                    max_length=100,)

    def AAAget_absolute_url(self):
        '''
        Returns the canonical URL to view a workout
        '''
        return reverse('manager.views.view_workout', kwargs={'id': self.id})

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "Association %s" % self.state.short_name

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    #class Meta:
    #    '''
    #    Metaclass to set some other properties
    #    '''
    #    ordering = ["-creation_date", ]
