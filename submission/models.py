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
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class BankAccount(models.Model):
    '''
    Model for a bank account
    '''

    owner_name = models.CharField(verbose_name=_('Owner name'),
                            max_length=100,)
    account_nr = models.CharField(verbose_name=_('Account nr.'),
                                  max_length=9,)
    bank_nr = models.CharField(verbose_name=_('Bank nr.'),
                               max_length=8,)
    bank_name = models.CharField(verbose_name=_('Bank name'),
                                 max_length=30,)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s, BLZ: %s" % (self.account_nr, self.bank_nr)


class State(models.Model):
    '''
    Model for a state
    '''

    name = models.CharField(verbose_name=_('Name'),
                            max_length=100,)
    short_name = models.CharField(verbose_name=_('Short name'),
                                  max_length=2,)
    bank_account = models.ForeignKey(BankAccount, verbose_name=_('Bank account'))

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

    def get_absolute_url(self):
        return reverse('gym-view', kwargs={'pk': self.id})


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
