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

# Standard Library
import logging
from email.mime.application import MIMEApplication
from functools import wraps

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_save
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# dbfv
from submission.helpers import build_starter_pdf, build_judge_pdf

logger = logging.getLogger(__name__)


class ManagerEmail(models.Model):
    """
    Emails to be notified when a new submission is entered
    """

    email = models.EmailField(_(u'Email'), max_length=30)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.email


class BankAccount(models.Model):
    """
    Model for a bank account
    """

    owner_name = models.CharField(
        verbose_name='Begünstigter',
        max_length=100,
    )
    iban = models.CharField(
        verbose_name='IBAN',
        max_length=34,
    )
    bic = models.CharField(
        verbose_name='BIC', max_length=11, help_text=u'Nur bei Auslandsüberweisung nötig'
    )
    bank_name = models.CharField(
        verbose_name='Bankname',
        max_length=30,
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "%s, BIC: %s" % (self.iban, self.bic)


class State(models.Model):
    """
    Model for a state
    """

    name = models.CharField(
        verbose_name='Name',
        max_length=100,
    )
    short_name = models.CharField(
        verbose_name='Kürzel',
        max_length=3,
    )
    email = models.EmailField(verbose_name='Email', max_length=120, blank=True)
    bank_account = models.ForeignKey(
        BankAccount, verbose_name='Bankkonto', on_delete=models.CASCADE
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name


class Gym(models.Model):
    """
    Model for a gym
    """

    class Meta:
        """
        Order first by state name, then by gym name
        """
        ordering = ["state__name", "name"]

    # Properties
    name = models.CharField(
        verbose_name='Name',
        max_length=100,
    )
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    state = models.ForeignKey(State, verbose_name='Bundesland', on_delete=models.CASCADE)

    owner = models.CharField(verbose_name='Inhaber', max_length=100, blank=True, null=True)
    zip_code = models.IntegerField(_(u'PLZ'), blank=True, null=True)
    city = models.CharField(_(u'Ort'), max_length=30, blank=True, null=True)
    street = models.CharField(_(u'Straße'), max_length=30, blank=True, null=True)
    is_active = models.BooleanField(_('Ist aktiv'), default=True)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return u"{0} ({1}, {2})".format(self.name, self.city, self.state)

    def get_absolute_url(self):
        return reverse('gym-view', kwargs={'pk': self.id})


class Country(models.Model):
    """
    Model for a country
    """

    # This field is required.
    name = models.CharField(max_length=40)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name


def attachment_submission_dir(instance, filename):
    return "anlagen/antrag/%s/%s/%s" % (instance.gym.state.short_name, instance.gym_id, filename)


#
#
# Submissions
#
#
class AbstractSubmission(models.Model):
    """
    Abstract class with fields and logic common to all submissions types
    (starter, gym and judge)
    """

    class Meta:
        """
        This is an abstract class
        """
        abstract = True

    MAILMERGE_HEADER = []

    SUBMISSION_STATUS_EINGEGANGEN = '1'
    SUBMISSION_STATUS_BEWILLIGT = '2'
    SUBMISSION_STATUS_ABGELEHNT = '3'

    SUBMISSION_STATUS = (
        (SUBMISSION_STATUS_EINGEGANGEN, 'Eingegangen'),
        (SUBMISSION_STATUS_BEWILLIGT, 'Bewilligt'),
        (SUBMISSION_STATUS_ABGELEHNT, 'Abgelehnt'),
    )

    user = models.ForeignKey(User, verbose_name=_('User'), editable=False, on_delete=models.CASCADE)
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    submission_status = models.CharField(
        max_length=2, choices=SUBMISSION_STATUS, default=SUBMISSION_STATUS_EINGEGANGEN
    )
    mail_merge = models.BooleanField(default=False, editable=False)
    """Deprecated"""

    pdf_sent = models.BooleanField(default=False)
    """Flag indicating whether the athlete has received the confirmation PDF"""

    def get_bank_designated_use(self):
        """
        Returns the designated use to be used when doing the bank transfer
        """
        return u'{0} {1}<br>\n{2}'.format(self.get_license_type(), self.pk, self.get_name)

    def get_email_list(self):
        """
        Collects and returns a list with the recipients of notification emails
        """
        raise NotImplementedError('You must implement this method in derived classes')

    def get_email_subject(self):
        """
        Returns the subject for the notification email
        """
        return u'Neue {0} beantragt von {1}'.format(self.get_license_type(), self.get_name)

    def get_email_template(self):
        """
        Returns the template used for the notification email
        """
        raise NotImplementedError('You must implement this method in derived classes')

    @staticmethod
    def get_license_type():
        """
        Returns the name of the license, this is used e.g. in the email subject
        """
        raise NotImplementedError('You must implement this method in derived classes')

    def get_search_json(self):
        """
        Returns the necessary JSON to be used in the search
        """
        return {
            'id': self.id,
            'name': self.get_name,
            'status': self.get_submission_status_display(),
            'date': self.creation_date.strftime("%d.%m.%Y")
        }

    def notification_email_hook(self):
        """
        Hook to perform custom logic after sending the notification emails
        """
        pass

    def send_emails(self, extra_data=[]):
        """
        Email the managers
        """
        context = {'submission': self,
                   'fee': self.FEE,
                   'bankaccount': BankAccount.objects.get(pk=self.get_bank_account()),
                   'extra_data': extra_data}
        for email in self.get_email_list():

            if email == self.email:
                context['is_user'] = True
            else:
                context['is_user'] = False

            message = render_to_string(self.get_email_template(), context)
            mail.send_mail(
                self.get_email_subject(),
                message,
                settings.DEFAULT_FROM_EMAIL, [email],
                fail_silently=True
            )

        # Perform custom logic
        self.notification_email_hook()

    def get_mailmerge_row(self):
        """
        Returns a row for the mailmerge CSV export
        """
        raise NotImplementedError('You must implement this method in derived classes')


class SubmissionStarter(AbstractSubmission):
    """
    Model for a submission
    """

    class Meta:
        """
        Order first by state name, then by gym name
        """
        ordering = ["creation_date", "gym"]

    MAILMERGE_HEADER = [
        'ID', 'Vorname', 'Nachname', 'Geburtsdatum', 'Aktiv Seit', 'Straße', 'Hausnummer', 'PLZ',
        'Stadt', 'Telefon', 'Email', 'Nationalität', 'Größe', 'Gewicht', 'Kategorie', 'Studio',
        'Bundesverband', 'Datum', 'Jahr'
    ]

    SUBMISSION_CATEGORY = (
        ('1', u'Bikini-Fitness Klasse I'),
        ('19', u'Bikini-Fitness Klasse II'),
        ('20', u'Bikini-Fitness Klasse III'),
        ('21', u'Frauen Wellness Klasse'),
        ('2', u'Frauen Fitness-Figur Klasse I'),
        ('22', u'Frauen Fitness-Figur Klasse II'),
        # ('3', u'Frauen Bodyklasse'),
        ('4', u'Frauen Physique'),
        # ('5', u'Juniorenklasse'),
        ('6', u'Classic-Bodybuilding Klasse I'),
        ('23', u'Classic-Bodybuilding Klasse II'),
        ('30', u'Classic Physique'),
        ('7', u'Paare'),
        ('31', u'Fit Pairs'),
        ('8', u'Männer Physique Klassse I'),
        ('24', u'Männer Physique Klasse II'),
        ('25', u'Männer Physique Klasse III'),
        # ('9', u'Männer Bodyklasse'),
        # ('10', u'Wellness-Fitness'),
        ('11', u'Muscular-Physique'),
        # ('12', u'Masters-Männer BB'),
        ('26', u'Männer Klasse I'),
        ('27', u'Männer Klasse II'),
        ('28', u'Männer Klasse III'),
        ('29', u'Männer Klasse IV'),
        ('30', u'Männer Klasse V'),
        # ('13', u'Masters-Männer Classic BB'),
        # ('14', u'Masters-Männer Physique'),
        # ('15', u'Masters-Frauen Physique'),
        # ('16', u'Masters-Frauen Bikini Fitness'),
        # ('17', u'Masters-Frauen Figur'),
    )
    # Commented out: out = [3, 5, 9, 10, 12, 13, 14, 15, 16, 17]

    FEE = 90

    # Personal information
    date_of_birth = models.DateField(_('Geburtsdatum'))
    active_since = models.CharField(_('Aktiv seit'), max_length=20)
    last_name = models.CharField(_('Familienname'), max_length=30)
    first_name = models.CharField(_('Vorname'), max_length=30)
    street = models.CharField(_(u'Straße'), max_length=30)
    house_nr = models.CharField(_(u'Hausnummer'), max_length=30)
    zip_code = models.IntegerField(_(u'PLZ'))
    city = models.CharField(_(u'Ort'), max_length=30)
    tel_number = models.CharField(_(u'Tel. Nr.'), max_length=20)
    email = models.EmailField(_(u'Email'), max_length=120)
    nationality = models.ForeignKey(
        Country,
        verbose_name=u'Staatsangehörigkeit',
        default=37,  # Germany
        on_delete=models.CASCADE
    )
    height = models.IntegerField(_(u'Größe (cm)'))
    weight = models.DecimalField(_(u'Wettkampfgewicht (kg)'), max_digits=5, decimal_places=2)
    category = models.CharField(
        _(u'Kategorie'),
        max_length=2,
        choices=SUBMISSION_CATEGORY,
    )
    terms_and_conditions = models.BooleanField(
        'Hiermit erkläre ich mich mit den Regeln des DBFV e.V.', blank=False
    )

    # Other fields
    submission_last_year = models.BooleanField(
        u"Im Vorjahr wurde bereits eine Lizenz beantragt", default=False
    )

    gym = models.ForeignKey(Gym, verbose_name='Studio', on_delete=models.CASCADE)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "%s - %s" % (self.creation_date, self.user)

    def get_absolute_url(self):
        return reverse('submission-view', kwargs={'pk': self.pk})

    @property
    def get_name(self):
        """
        Returns the name of the participant
        """
        return u"{0}, {1}".format(self.last_name, self.first_name)

    def get_bank_account(self):
        """
        Returns the correct bank account for this submission
        """
        bank_account = 1
        if self.gym.state_id == 10:
            bank_account = 2

        return bank_account

    @staticmethod
    def get_license_type():
        """
        Returns the name of the license, this is used e.g. in the email subject
        """
        return 'Starterlizenz'

    @staticmethod
    def get_email_template():
        """
        Returns the template used for the notification email
        """
        return 'submission/starter/email_new_submission.html'

    def send_pdf_email(self):
        """
        Sends the confirmation PDF to the user
        """
        email_subject = f'Starterlizenz {self.creation_date.year}'
        email_text = f"""Sehr geeehrte Dame, sehr geehrter Herr {self.last_name},
        
mit dieser E-Mail erhalten Sie ihre beantragte Starterlizenz des DBFV e. V. für
das Kalenderjahr {self.creation_date.year}.

Wir wünschen Ihnen eine gute Vorbereitung und viel Spaß und Erfolg bei der
Teilnahme an unseren Meisterschaften.

Ihr DBFV e. V.
        """
        logger.info(f'Sending PDF for submission {self.id} - ({self.user.email})')
        msg = EmailMultiAlternatives(
            email_subject,
            email_text,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
        )
        msg.mixed_subtype = 'related'

        # Build the PDF and attach it to the email
        response = HttpResponse(content_type='application/pdf')
        build_starter_pdf(HttpRequest(), self, response)
        msg_part = MIMEApplication(response.content)
        msg_part['Content-Disposition'] = f'attachment; filename="Starterlizenz-{self.id}.pdf"'
        msg.attach(msg_part)

        # Send the email
        msg.send()

    def get_email_list(self):
        """
        Collects and returns a list with the recipients of notification emails
        """
        email_list = []
        for email in ManagerEmail.objects.all():
            email_list.append(email.email)

        if self.gym.email:
            email_list.append(self.gym.email)

        if self.gym.state.email:
            email_list.append(self.gym.state.email)

        # Hamburg
        if self.gym.state.pk == 6:
            email_list.append('clausmaibaum@web.de')

        # Hessen
        if self.gym.state.pk == 7:
            email_list.append('info@hbbkv.com')

        # Bayern
        if self.gym.state.pk == 2:
            email_list.append('lambert.boehm@blv-bfk.de')

        email_list.append(self.email)
        return email_list

    def notification_email_hook(self):
        """
        Notify the managers if the selected gym has no email
        """
        if not self.gym.email:
            for email in ManagerEmail.objects.all():
                mail.send_mail(
                    'Studio hat keine Emailadresse',
                    u"Eine Starterlizenz wurde für ein Studio beantragt, dass\n"
                    u"keine Emailadresse im System hinterlegt hat.\n\n"
                    u"* Nr.:        {studio.pk}\n"
                    u"* Name:       {studio.name}\n"
                    u"* Bundesland: {studio.state.name}\n".format(studio=self.gym),
                    settings.DEFAULT_FROM_EMAIL, [email.email],
                    fail_silently=True
                )

    def get_search_json(self):
        """
        Returns the necessary JSON to be used in the search
        """
        data = super(SubmissionStarter, self).get_search_json()
        data['state'] = self.gym.state.name
        data['category'] = self.get_category_display()
        data['gym'] = self.gym.name
        return data

    def get_mailmerge_row(self):
        """
        Returns a row for the mailmerge CSV export
        """
        return [
            self.pk,
            self.first_name,
            self.last_name,
            self.date_of_birth,
            self.active_since,
            self.street,
            self.house_nr,
            self.zip_code,
            self.city,
            self.tel_number,
            self.email,
            self.nationality.name,
            self.height,
            self.weight,
            self.get_category_display(),
            self.gym.name,
            self.gym.state,
            self.creation_date,
            self.creation_date.year,
        ]

    def save(self, *args, **kwargs):
        """
        For existing submissions, if we change the status to approved, email the user
        """
        if self.pk and self.submission_status == self.SUBMISSION_STATUS_BEWILLIGT:
            self.send_pdf_email()
            self.pdf_sent = True

        super().save(*args, **kwargs)


class SubmissionInternational(AbstractSubmission):
    """
    Model for a submission
    """

    class Meta:
        """
        Order first by state name, then by gym name
        """
        ordering = ["creation_date", "gym"]

    MAILMERGE_HEADER = [
        'ID', 'Vorname', 'Nachname', 'Geburtsdatum', 'Aktiv Seit', 'Straße', 'PLZ', 'Stadt',
        'Telefon', 'Email', 'Nationalität', 'Größe', 'Gewicht', 'Kategorie', 'Studio',
        'Bundesverband', 'Datum', 'Jahr', 'Meisterschaft', 'Datum der Meisterschaft'
    ]

    SUBMISSION_CATEGORY = (
        ('1', u'Jugend-Bikini-Fitness'),
        ('2', u'Jugend-Mens Physique'),
        ('3', u'Jugend-Bodybuilding'),
        ('4', u'Junioren-Bikini-Fitness'),
        ('5', u'Junioren-Mens Physique'),
        ('6', u'Junioren-Bodybuilding'),
        ('23', u'Junioren-Classic Bodybuilding'),
        ('21', u'Junioren-Frauen Fitness Figur'),
        ('22', u'Junioren-Frauen Physique'),
        ('7', u'Frauen-Bikini-Fitness'),
        ('25', u'Frauen-Wellness'),
        ('8', u'Frauen-Fitness-Figur'),
        ('9', u'Frauen-Physique'),
        ('10', u'Paare'),
        ('11', u'Handicappt/Wheelchair'),
        ('12', u'Classic Bodybuilding'),
        ('24', u'Classic Physique'),
        ('13', u'Männer Physique'),
        ('24', u'Männer Muscular Physique'),
        ('14', u'Männer Bodybuilding'),
        ('15', u'Masters-Männer BB'),
        ('16', u'Masters-Männer Classic BB'),
        ('17', u'Masters-Männer Physique'),
        ('18', u'Masters-Frauen Physique'),
        ('19', u'Masters-Frauen Bikini Fitness'),
        ('20', u'Masters-Frauen Figur'),
    )

    FEE = 0

    # Personal information
    date_of_birth = models.DateField(_('Geburtsdatum'))
    last_name = models.CharField(_('Familienname'), max_length=30)
    first_name = models.CharField(_('Vorname'), max_length=30)
    street = models.CharField(_(u'Straße'), max_length=30)
    zip_code = models.IntegerField(_(u'PLZ'))
    city = models.CharField(_(u'Ort'), max_length=30)
    tel_number = models.CharField(_(u'Tel. Nr.'), max_length=20)
    email = models.EmailField(_(u'Email'), max_length=120)
    nationality = models.ForeignKey(
        Country,
        verbose_name=u'Staatsangehörigkeit',
        default=37,  # Germany
        on_delete=models.CASCADE
    )
    height = models.IntegerField(_(u'Größe (cm)'))
    weight = models.DecimalField(_(u'Wettkampfgewicht in kg (ca.)'), max_digits=5, decimal_places=2)
    category = models.CharField(_(u'Kategorie'), max_length=100)
    championship = models.CharField(
        _(u'Meisterschaft'), help_text=u'Meisterschaft in der Du starten möchtest', max_length=150
    )
    championship_date = models.DateField(_(u'Datum der Meisterschaft'))

    best_placement = models.CharField(
        u'Beste Platzierung',
        max_length=150,
        help_text='Beste Platzierung auf einer deutschen '
        'DBFV/IFBB-Meisterschaft, mit Datum und Kategorie'
    )

    gym = models.ForeignKey(Gym, verbose_name='Studio', on_delete=models.CASCADE)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "%s - %s" % (self.creation_date, self.user)

    def get_absolute_url(self):
        return reverse('submission-international-view', kwargs={'pk': self.pk})

    @property
    def get_name(self):
        """
        Returns the name of the participant
        """
        return u"{0}, {1}".format(self.last_name, self.first_name)

    def get_bank_account(self):
        """
        Returns the correct bank account for this submission
        """
        bank_account = 1
        if self.gym.state_id == 10:
            bank_account = 2

        return bank_account

    @staticmethod
    def get_license_type():
        """
        Returns the name of the license, this is used e.g. in the email subject
        """
        return 'Internationaler Start'

    def get_email_template(self):
        """
        Returns the template used for the notification email
        """
        return 'submission/international/email_new_submission.html'

    def get_email_list(self):
        """
        Collects and returns a list with the recipients of notification emails
        """
        email_list = [
            'info@dbfv.de', 'dbfv.falk@gmail.com', "Margret.Netack@t-online.de", self.email
        ]
        if self.gym.state.email:
            email_list.append(self.gym.state.email)
        return email_list

    def notification_email_hook(self):
        """
        Notify the managers if the selected gym has no email
        """
        if not self.gym.email:
            for email in ManagerEmail.objects.all():
                mail.send_mail(
                    'Studio hat keine Emailadresse',
                    u"Eine internationale Lizenz wurde für ein Studio beantragt, dass\n"
                    u"keine Emailadresse im System hinterlegt hat.\n\n"
                    u"* Nr.:        {studio.pk}\n"
                    u"* Name:       {studio.name}\n"
                    u"* Bundesland: {studio.state.name}\n".format(studio=self.gym),
                    settings.DEFAULT_FROM_EMAIL, [email.email],
                    fail_silently=True
                )

    def get_search_json(self):
        """
        Returns the necessary JSON to be used in the search
        """
        data = super().get_search_json()
        data['state'] = self.gym.state.name
        data['category'] = self.category
        data['gym'] = self.gym.name
        return data

    def get_mailmerge_row(self):
        """
        Returns a row for the mailmerge CSV export
        """
        return [
            self.pk, self.first_name, self.last_name, self.date_of_birth,
            self.street, self.zip_code, self.city, self.tel_number, self.email,
            self.nationality.name, self.height, self.weight,
            self.category, self.gym.name, self.gym.state, self.creation_date,
            self.creation_date.year, self.championship, self.championship_date
        ]


class SubmissionGym(AbstractSubmission):
    """
    Model for a gym submission
    """
    class Meta:
        """
        Order first by state name, then by gym name
        """
        ordering = ["creation_date", "state"]

    FEE = 30

    # Personal information
    state = models.ForeignKey(State, verbose_name=_(u'Landesverband'), on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_('Name'), max_length=30, help_text=_('Name des Studios oder Verein')
    )
    owner = models.CharField(
        verbose_name='Inhaber', max_length=30,
    )
    founded = models.DateField(_(u'Gegründet am'))
    street = models.CharField(_(u'Straße'), max_length=30)
    zip_code = models.IntegerField(_(u'PLZ'))
    city = models.CharField(_(u'Ort'), max_length=30)
    tel_number = models.CharField(_(u'Tel. Nr.'), max_length=20)
    email = models.EmailField(_(u'Email'), max_length=120)

    # Other fields
    gym = models.OneToOneField(
        Gym, verbose_name='Studio', editable=False, blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return u"Studiolizenz {0}".format(self.get_name)

    def get_absolute_url(self):
        return reverse('submission-studio-view', kwargs={'pk': self.pk})

    @property
    def get_name(self):
        """
        Returns the name of the participant
        """
        return self.name

    def get_bank_account(self):
        """
        Returns the correct bank account for this submission
        """
        return self.state.bank_account.pk

    @staticmethod
    def get_license_type():
        """
        Returns the name of the license, this is used e.g. in the email subject
        """
        return 'Studiolizenz'

    def get_email_template(self):
        """
        Returns the template used for the notification email
        """
        return 'submission/gym/email_new_submission.html'

    def get_email_list(self):
        """
        Collects and returns a list with the recipients of notification emails
        """
        email_list = []
        for email in ManagerEmail.objects.all():
            email_list.append(email.email)

        if self.state.email:
            email_list.append(self.state.email)

        email_list.append(self.email)
        return email_list


class SubmissionJudge(AbstractSubmission):
    """
    Model for a judge submission
    """
    class Meta:
        """
        Order first by state name, then by gym name
        """
        ordering = ["creation_date", "state"]

    MAILMERGE_HEADER = [
        'ID', 'Vorname', 'Nachname', 'Straße', 'PLZ', 'Stadt', 'Telefon', 'Email', 'Bundesverband',
        'Datum', 'Jahr'
    ]

    FEE = 20

    last_name = models.CharField('Familienname', max_length=30)
    first_name = models.CharField('Vorname', max_length=30)
    street = models.CharField(u'Straße', max_length=30)
    zip_code = models.IntegerField(u'PLZ')
    city = models.CharField(u'Ort', max_length=30)
    state = models.ForeignKey(State, verbose_name=u'Landesverband', on_delete=models.CASCADE)
    tel_number = models.CharField(u'Tel. Nr.', max_length=20)
    email = models.EmailField(u'Email', max_length=120, null=True, blank=True)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return u"Kampfrichterlizenz {0}".format(self.get_name)

    def get_absolute_url(self):
        return reverse('submission-judge-view', kwargs={'pk': self.pk})

    @property
    def get_name(self):
        """
        Returns the name of the participant
        """
        return u"{0}, {1}".format(self.last_name, self.first_name)

    def get_bank_account(self):
        """
        Returns the correct bank account for this submission
        """
        bank_account = 1
        if self.state.pk == 10:
            bank_account = 2

        return bank_account

    @staticmethod
    def get_license_type():
        """
        Returns the name of the license, this is used e.g. in the email subject
        """
        return 'Kampfrichterlizenz'

    def get_email_template(self):
        """
        Returns the template used for the notification email
        """
        return 'submission/judge/email_new_submission.html'

    def get_email_list(self):
        """
        Collects and returns a list with the recipients of notification emails
        """
        email_list = []
        for email in ManagerEmail.objects.all():
            email_list.append(email.email)

        if self.state.email:
            email_list.append(self.state.email)

        email_list.append(self.email)
        email_list.append('kampfrichter@dbfv.de')

        # Hamburg
        if self.state.pk == 6:
            email_list.append('clausmaibaum@web.de')

        return email_list

    def get_mailmerge_row(self):
        """
        Returns a row for the mailmerge CSV export
        """
        return [
            self.pk, self.first_name, self.last_name, self.street, self.zip_code, self.city,
            self.tel_number, self.email, self.state.name, self.creation_date,
            self.creation_date.year
        ]

    def send_pdf_email(self):
        """
        Sends the confirmation PDF to the user
        """
        email_subject = f'Kampfrichterlizenz {self.creation_date.year}'
        email_text = f"""Sehr geeehrte Dame, sehr geehrter Herr {self.last_name},

mit dieser E-Mail erhalten Sie ihre beantragte Kampfrichterlizenz des DBFV e. V. für
das Kalenderjahr {self.creation_date.year}.

Wir wünschen Ihnen eine gute Vorbereitung und viel Spaß und Erfolg bei der
Teilnahme an unseren Meisterschaften.

Ihr DBFV e. V.
        """
        logger.info(f'Sending PDF for judge submission {self.id} - ({self.user.email})')
        msg = EmailMultiAlternatives(
            email_subject,
            email_text,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
        )
        msg.mixed_subtype = 'related'

        # Build the PDF and attach it to the email
        response = HttpResponse(content_type='application/pdf')
        build_judge_pdf(HttpRequest(), self, response)
        msg_part = MIMEApplication(response.content)
        msg_part['Content-Disposition'] = f'attachment; filename="Starterlizenz-{self.id}.pdf"'
        msg.attach(msg_part)

        # Send the email
        msg.send()

    def save(self, *args, **kwargs):
        """
        For existing submissions, if we change the status to approved, email the user
        """
        if self.pk and self.submission_status == self.SUBMISSION_STATUS_BEWILLIGT:
            self.send_pdf_email()
            self.pdf_sent = True

        super().save(*args, **kwargs)


USER_TYPE_UNKNOWN = -1
USER_TYPE_BUNDESVERBAND = 2
USER_TYPE_USER = 3
USER_TYPES = (
    (USER_TYPE_BUNDESVERBAND, u'Bundesverband'),
    (USER_TYPE_USER, u'User'),
    (USER_TYPE_UNKNOWN, u'Unbekannt'),
)


class UserProfile(models.Model):
    """
    Model for a user's profile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    email_verified = models.BooleanField(default=False)
    """Flag indicating whether the user's email has been verified"""

    # User type
    type = models.IntegerField(choices=USER_TYPES, default=USER_TYPE_USER)

    # Personal information
    state = models.ForeignKey(State, blank=True, null=True, on_delete=models.CASCADE)

    terms_and_conditions = models.BooleanField(
        'Hiermit erkläre ich mich mit den Regeln des DBFV e.V.', blank=False, default=False
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return 'Profile for %s' % self.user.username


def disable_for_loaddata(signal_handler):
    """
    Decorator to prevent clashes when loading data with loaddata and
    post_connect signals. See also:
    http://stackoverflow.com/questions/3499791/how-do-i-prevent-fixtures-from-conflicting
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs['raw']:
            # print "Skipping signal for {0} {1}".format(args, kwargs)
            return
        signal_handler(*args, **kwargs)

    return wrapper


# Every new user gets a profile
@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


def user_profile(user):
    """
    Return the profile of user or None if the user is not authenticated.
    """
    if not user.is_authenticated:
        return None

    # for authenticated users, look into the profile.
    return user.userprofile


def user_type(user):
    """
    Return the type of user or None if the user is not authenticated.
    """
    profile = user_profile(user)
    if profile is None:
        return None

    return profile.type
