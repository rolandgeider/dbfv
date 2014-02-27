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
        return "%s, BIC: %s" % (self.iban, self.bic)


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
    is_active = models.BooleanField(_('Ist aktiv'),
                                    default=True)


    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} ({1}, {2})".format(self.name, self.city, self.state)

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
    name = models.CharField(max_length=40)

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

    SUBMISSION_STATUS_EINGEGANGEN = '1'
    SUBMISSION_STATUS_BEWILLIGT = '2'
    SUBMISSION_STATUS_ABGELEHNT = '3'

    SUBMISSION_STATUS = (
        (SUBMISSION_STATUS_EINGEGANGEN, 'Eingegangen'),
        (SUBMISSION_STATUS_BEWILLIGT, 'Bewilligt'),
        (SUBMISSION_STATUS_ABGELEHNT, 'Abgelehnt'),
    )
    SUBMISSION_CATEGORY = (
        ('1', u'Bikini-Klasse'),
        ('2', u'Frauen Fitness-Figur-Klasse'),
        ('3', u'Frauen Bodyklasse'),
        ('4', u'Frauen Physiqueklasse'),
        ('5', u'Juniorenklasse'),
        ('6', u'Classic-Bodybuilding'),
        ('7', u'Paare'),
        ('8', u'Männer Physique'),
        ('9', u'Männer Bodyklasse')
    )

    FEE = 50

    # Personal information
    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)

    date_of_birth = models.DateField(_('Geburtsdatum'))
    active_since = models.CharField(_('Aktiv seit'), max_length=20)
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
    submission_last_year = models.BooleanField(u"Im Vorjahr wurde bereits eine Lizenz beantragt",
                                               default=False)

    gym = models.ForeignKey(Gym, verbose_name='Studio')

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
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
            lizenz_vorjahr = 'Ja' if self.submission_last_year else 'Nein'
            subject = _(u'Neue Starterlizenz beantragt von {0}, {1}'.format(self.last_name,
                                                                            self.first_name))
            message = (u"Eine neue Starterlizenz wurde beantragt\n"
                       u"---------------------------------------\n\n"
                       u"Details:\n"
                       u"* Antragsnummer:         {data.pk}\n"
                       u"* Name:                  {data.last_name}\n"
                       u"* Vorname:               {data.first_name}\n"
                       u"* Geburtsdatum:          {data.date_of_birth}\n"
                       u"* Adresse:               {data.street}, {data.city}, {data.zip_code}\n"
                       u"* Staatsangehörigkeit:   {data.nationality}\n"
                       u"* Email:                 {data.email}\n"
                       u"* Telefon:               {data.tel_number}\n"
                       u"* Größe (cm):            {data.height}\n"
                       u"* Wettkampfgewicht (kg): {data.weight}\n"
                       u"* Klasse:                {category}\n"
                       u"* Lizenz im Vorjahr:     {lizenz_vorjahr}\n"
                       u"* Studio:                {data.gym.name} ({data.gym.state.name})\n"
                       u"                         {data.gym.email}\n\n"
                       u"".format(category=self.get_category_display(),
                                  lizenz_vorjahr=lizenz_vorjahr,
                                  data=self))
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


class SubmissionJudge(models.Model):
    '''
    Model for a judge submission
    '''

    SUBMISSION_STATUS_EINGEGANGEN = '1'
    SUBMISSION_STATUS_BEWILLIGT = '2'
    SUBMISSION_STATUS_ABGELEHNT = '3'

    SUBMISSION_STATUS = (
        (SUBMISSION_STATUS_EINGEGANGEN, 'Eingegangen'),
        (SUBMISSION_STATUS_BEWILLIGT, 'Bewilligt'),
        (SUBMISSION_STATUS_ABGELEHNT, 'Abgelehnt'),
    )

    FEE = 15


    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)
    last_name = models.CharField('Familienname', max_length=30)
    first_name = models.CharField('Vorname', max_length=30)
    street = models.CharField(u'Straße', max_length=30)
    zip_code = models.IntegerField(u'PLZ', max_length=5)
    city = models.CharField(u'Ort', max_length=30)
    state = models.ForeignKey(State,
                              verbose_name=u'Landesverband')
    tel_number = models.CharField(u'Tel. Nr.',
                                  max_length=20)
    email = models.EmailField(u'Email',
                              max_length=30,
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
        return u"Kampfrichterlizent {0}".format(self.name)

    def get_absolute_url(self):
        return reverse('submission-judge-view', kwargs={'pk': self.pk})

    @property
    def get_name(self):
        """
        Returns the name of the participant
        """
        return u"{0}, {1}".format(self.last_name, self.first_name)

    def send_emails(self):
        '''
        Send an email to the managers
        '''

        # Make a list with all the emails: BV, LV, gym and user
        email_list = []
        for email in ManagerEmail.objects.all():
            email_list.append(email.email)

        if self.state.email:
            email_list.append(self.state.email)

        email_list.append(self.user.email)

        for email in email_list:
            subject = _(u'Neue Kampfrichterlizenz von {0}, {1}'.format(self.last_name,
                                                                       self.first_name))
            message = (_(u"Eine neue Kampfrichterlizenz wurde beantragt\n"
                         u"--------------------------------------------\n\n"
                         u"Details:\n"
                         u"* Name:          {last_name}\n"
                         u"* Vorname:       {first_name}\n"
                         u"* Adresse:       {street}, {city}, {zip_code}\n"
                         u"* Tel. Nr.:      {tel_nr}\n"
                         u"* Landesverband: {state}\n"
                         u"").format(last_name=self.last_name,
                                     first_name=self.first_name,
                                     tel_nr=self.tel_number,
                                     street=self.street,
                                     city=self.city,
                                     zip_code=self.zip_code,
                                     state=self.state.name))
            mail.send_mail(subject,
                           message,
                           email,
                           [email],
                           fail_silently=True)

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
