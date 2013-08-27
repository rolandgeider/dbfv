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
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


class BankAccount(models.Model):
    '''
    Model for a bank account
    '''

    owner_name = models.CharField(verbose_name='Begünstigter',
                                  max_length=100,)
    account_nr = models.CharField(verbose_name='Kontonummer',
                                  max_length=9,)
    bank_nr = models.CharField(verbose_name='BLZ',
                               max_length=8,)
    bank_name = models.CharField(verbose_name='Bankname',
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

    name = models.CharField(verbose_name='Name',
                            max_length=100,)
    short_name = models.CharField(verbose_name='Kürzel',
                                  max_length=3,)
    bank_account = models.ForeignKey(BankAccount, verbose_name='Bankkonto')

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name


class Gym(models.Model):
    '''
    Model for a gym
    '''

    name = models.CharField(verbose_name='Name',
                            max_length=100,)
    email = models.EmailField(verbose_name='Email', blank=True)
    state = models.ForeignKey(State, verbose_name='Bundesland')

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s (%s)" % (self.name, self.state)

    def get_absolute_url(self):
        return reverse('gym-view', kwargs={'pk': self.id})

    # Metaclass to set some other properties
    class Meta:
        ordering = ["state__name", "name"]


class StateAssociation(models.Model):
    '''
    Model for a State Association (Landesverband)
    '''

    state = models.ForeignKey(State, verbose_name='Bundesland')
    bank_account = models.CharField(verbose_name='Name',
                                    max_length=100,)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "Association %s" % self.state.short_name



def attachment_submission_dir(instance, filename):

    return "anlagen/antrag/%s/%s/%s" % (instance.gym.state.short_name, instance.gym_id, filename)


class Submission(models.Model):
    '''
    Model for a submission
    '''
    SUBMISSION_TYPES = (
    ('ST', 'Starter'),
    ('KR', 'Kapmfrichter'),
    ('SU', 'Studio'),
    )

    SUBMISSION_STATUS_EINGEGANGEN = '1'
    SUBMISSION_STATUS_BEWILLIGT = '2'
    SUBMISSION_STATUS_ABGELEHNT = '3'

    SUBMISSION_STATUS = (
        (SUBMISSION_STATUS_EINGEGANGEN, 'Eingegangen'),
        (SUBMISSION_STATUS_BEWILLIGT, 'Bewilligt'),
        (SUBMISSION_STATUS_ABGELEHNT, 'Abgelehnt'),
    )


    gym = models.ForeignKey(Gym, verbose_name='Studio')
    anhang = models.FileField(upload_to=attachment_submission_dir,
                              verbose_name='Antrag',
                              help_text='Das ausgefüllte Antrags-PDF hier hochladen.')

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)
    submission_type = models.CharField(max_length=2,
                                       choices=SUBMISSION_TYPES,
                                       editable=False)
    submission_status_bv = models.CharField(max_length=2,
                                            choices=SUBMISSION_STATUS,
                                            default=SUBMISSION_STATUS_EINGEGANGEN)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s - %s" % (self.creation_date, self.user)


# Deleting a Submission object also deletes the file from disk
def delete_submission_attachment(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, instance.anhang))
    except Exception, e:
        pass
        #logger.error("Could not delete attachment", e)

post_delete.connect(delete_submission_attachment, sender=Submission)


USER_TYPE_UNKNOWN = -1
USER_TYPE_BUNDESVERBAND = 2
USER_TYPE_USER = 3
USER_TYPES = ((USER_TYPE_BUNDESVERBAND, u'Bundesverband'),
              (USER_TYPE_USER, u'User'),
              (USER_TYPE_UNKNOWN, u'Unbekannt'))


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # User type
    type = models.IntegerField(max_length=1,
                               choices=USER_TYPES,
                               default=USER_TYPE_UNKNOWN)

    # Foreign keys
    state = models.ForeignKey(State,
                              blank=True,
                              null=True)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return 'Profile for %s' % self.user.username


# Every new user gets a profile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)


def user_profile(user):
    '''
    Return the profile of user or None if the user is not authenticated.
    '''
    if user.is_anonymous():
        return None

    # for authenticated users, look into the profile.
    return user.get_profile()


def user_type(user):
    '''
    Return the type of user or None if the user is not authenticated.
    '''
    profile = user_profile(user)
    if profile is None:
        return None

    return profile.type
