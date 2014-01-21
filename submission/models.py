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
import datetime

from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core import mail


class ManagerEmail(models.Model):
    '''
    Emails to be notified when a new submission is entered
    '''

    email = models.EmailField(_(u'Email'), max_length=30)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.email


class BankAccount(models.Model):
    '''
    Model for a bank account
    '''

    owner_name = models.CharField(verbose_name='Begünstigter',
                                  max_length=100,)
    iban = models.CharField(verbose_name='IBAN',
                            max_length=34,)
    bic = models.CharField(verbose_name='BIC',
                           max_length=11,
                           help_text=u'Nur bei Auslandsüberweisung nötig')
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
    email = models.EmailField(verbose_name='Email',
                              blank=True)
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
    email = models.EmailField(verbose_name='Email',
                              blank=True,
                              null=True)
    state = models.ForeignKey(State, verbose_name='Bundesland')

    owner = models.CharField(verbose_name='Inhaber',
                             max_length=100,
                             blank=True,
                             null=True)
    zip_code = models.IntegerField(_(u'PLZ'),
                                   max_length=5,
                                   blank=True,
                                   null=True)
    city = models.CharField(_(u'Ort'),
                            max_length=30,
                            blank=True,
                            null=True)
    street = models.CharField(_(u'Straße'),
                              max_length=30,
                              blank=True,
                              null=True)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s (%s)" % (self.name, self.state)

    def get_absolute_url(self):
        return reverse('gym-view', kwargs={'pk': self.id})

    class Meta:
        '''
        Order first by state name, then by gym name
        '''
        ordering = ["state__name", "name"]


class Country(models.Model):
    '''
    Model for a country
    '''

    # This field is required.
    name = models.CharField(max_length=20)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name


def attachment_submission_dir(instance, filename):

    return "anlagen/antrag/%s/%s/%s" % (instance.gym.state.short_name, instance.gym_id, filename)


class SubmissionStarter(models.Model):
    '''
    Model for a submission
    '''
    SUBMISSION_TYPES = (
        ('ST', 'Starter'),
        ('KR', 'Kapmfrichter'),
        ('SU', 'Studio')
    )

    SUBMISSION_STATUS_EINGEGANGEN = '1'
    SUBMISSION_STATUS_BEWILLIGT = '2'
    SUBMISSION_STATUS_ABGELEHNT = '3'

    SUBMISSION_STATUS = (
        (SUBMISSION_STATUS_EINGEGANGEN, 'Eingegangen'),
        (SUBMISSION_STATUS_BEWILLIGT, 'Bewilligt'),
        (SUBMISSION_STATUS_ABGELEHNT, 'Abgelehnt'),
    )
    SUBMISSION_CATEGORY = (
        ('1', u'Bodybuilding Frauen/Männer/Junioren/Master'),
        ('2', u'Frauen Bikini-Fitness'),
        ('3', u'Figurklasse'),
        ('4', u'Physique'),
        ('5', u'Classic-Bodybuilding'),
        ('6', u'Paare')
    )

    FEE = 50

    # Personal information
    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)

    date_of_birth = models.DateField(_('Geburtsdatum'))
    active_since = models.DateField(_('Aktiv seit'))
    last_name = models.CharField(_('Familienname'), max_length=30)
    first_name = models.CharField(_('Vorname'), max_length=30)
    street = models.CharField(_(u'Straße'), max_length=30)
    zip_code = models.IntegerField(_(u'PLZ'), max_length=5)
    city = models.CharField(_(u'Ort'), max_length=30)
    tel_number = models.CharField(_(u'Tel. Nr.'), max_length=20)
    email = models.EmailField(_(u'Email'), max_length=30)
    nationality = models.ForeignKey(Country,
                                    verbose_name=u'Staatsangehörigkeit',
                                    default=37  # Germany
                                    )
    height = models.IntegerField(_(u'Größe (cm)'), max_length=3)
    weight = models.DecimalField(_(u'Wettkampfgewicht (kg)'),
                                 max_digits=5,
                                 decimal_places=2)
    category = models.CharField(_(u'Kategorie'),
                                max_length=1,
                                choices=SUBMISSION_CATEGORY)

    # Other fields
    gym = models.ForeignKey(Gym, verbose_name='Studio')

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    #submission_type = models.CharField(max_length=2,
    #                                   choices=SUBMISSION_TYPES,
    #                                   editable=False)
    submission_status = models.CharField(max_length=2,
                                         choices=SUBMISSION_STATUS,
                                         default=SUBMISSION_STATUS_EINGEGANGEN)
    mail_merge = models.BooleanField(default=False,
                                     editable=False)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s - %s" % (self.creation_date, self.user)

    class Meta:
        '''
        Order first by state name, then by gym name
        '''
        ordering = ["creation_date", "gym"]

    @property
    def get_name(self):
        """
        Returns the name of the participant
        """
        return u"{0}, {1}".format(self.last_name, self.first_name)

    def get_absolute_url(self):
        return reverse('submission-view', kwargs={'pk': self.pk})

    def send_emails(self):
        '''
        Send an email to the managers
        '''

        # Make a list with all the emails: BV, LV, gym and user
        email_list = []
        for email in ManagerEmail.objects.all():
            email_list.append(email.email)

        if self.gym.email:
            email_list.append(self.gym.email)

        if self.gym.state.email:
            email_list.append(self.gym.state.email)

        email_list.append(self.user.email)

        for email in email_list:
            subject = _(u'Neue Starterlizenz beantragt von {0}, {1}'.format(self.last_name,
                                                                            self.first_name))
            message = (_(u"Eine neue Starterlizenz wurde beantragt\n"
                         u"---------------------------------------\n\n"
                         u"Details:\n"
                         u"* Name:                  {last_name}\n"
                         u"* Vorname:               {first_name}\n"
                         u"* Geburtsdatum:          {date_of_birth}\n"
                         u"* Adresse:               {street}, {city}, {zip_code}\n"
                         u"* Staatsangehörigkeit:   {nationality}\n"
                         u"* Größe (cm):            {height}\n"
                         u"* Wettkampfgewicht (kg): {weight}\n"
                         u"* Klasse:                {category}\n"
                         u"* Studio:                {gym} ({state})\n\n"
                         u"").format(last_name=self.last_name,
                                     first_name=self.first_name,
                                     date_of_birth=self.date_of_birth,
                                     category=self.get_category_display(),
                                     street=self.street,
                                     height=self.height,
                                     weight=self.weight,
                                     nationality=self.nationality,
                                     city=self.city,
                                     zip_code=self.zip_code,
                                     gym=self.gym.name,
                                     state=self.gym.state.name))
            mail.send_mail(subject,
                           message,
                           email,
                           [email],
                           fail_silently=True)


class SubmissionGym(models.Model):
    '''
    Model for a gym submission
    '''

    SUBMISSION_STATUS_EINGEGANGEN = '1'
    SUBMISSION_STATUS_BEWILLIGT = '2'
    SUBMISSION_STATUS_ABGELEHNT = '3'

    SUBMISSION_STATUS = (
        (SUBMISSION_STATUS_EINGEGANGEN, 'Eingegangen'),
        (SUBMISSION_STATUS_BEWILLIGT, 'Bewilligt'),
        (SUBMISSION_STATUS_ABGELEHNT, 'Abgelehnt'),
    )

    # Personal information
    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)

    state = models.ForeignKey(State,
                              verbose_name=_(u'Landesverband'))
    name = models.CharField(verbose_name=_('Name'),
                            max_length=30,
                            help_text=_('Name des Studios oder Verein'))
    founded = models.DateField(_(u'Gegründet am'))
    street = models.CharField(_(u'Straße'), max_length=30)
    zip_code = models.IntegerField(_(u'PLZ'), max_length=5)
    city = models.CharField(_(u'Ort'), max_length=30)
    tel_number = models.CharField(_(u'Tel. Nr.'), max_length=20)
    fax_number = models.CharField(_(u'Fax. Nr.'), max_length=20)
    email = models.EmailField(_(u'Email'), max_length=30)
    members = models.IntegerField(verbose_name=_(u'Anzahl Mitglieder'),
                                  max_length=5,
                                  help_text=_('Dient nur statistischen Zwecken'),
                                  null=True,
                                  blank=True)

    # Other fields
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    submission_status = models.CharField(max_length=2,
                                         choices=SUBMISSION_STATUS,
                                         default=SUBMISSION_STATUS_EINGEGANGEN)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Studiolizent {0}".format(self.name)

## Deleting a Submission object also deletes the file from disk
#def delete_submission_attachment(sender, instance, **kwargs):
    #try:
        #os.remove(os.path.join(settings.MEDIA_ROOT, instance.anhang))
    #except Exception, e:
        #pass
        ##logger.error("Could not delete attachment", e)

#post_delete.connect(delete_submission_attachment, sender=Submission)


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
