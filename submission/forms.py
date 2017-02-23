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
from django.core.exceptions import ValidationError

from django.forms import (
    ModelForm,
    MultipleChoiceField,
    EmailField,
    BooleanField,
    ModelChoiceField
)
from django.contrib.auth.models import User as Django_User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _

from captcha.fields import ReCaptchaField

from submission.models import (
    State,
    Gym,
    SubmissionStarter,
    SubmissionGym,
    SubmissionJudge,
    SubmissionInternational
)


class UserEmailForm(ModelForm):
    email = EmailField(label=_("Email"),
                       help_text=u"Wird nur gebraucht, wenn Sie das Passwort vergessen "
                                 u"und zurücksetzen müssen",
                       required=False)

    def clean_email(self):
        # Email must be unique systemwide
        email = self.cleaned_data["email"]
        if not email:
            return email
        try:
            Django_User.objects.get(email=email)
        except Django_User.DoesNotExist:
            return email
        raise ValidationError(u"Diese Email wird bereits benutzt.")


class RegistrationForm(UserCreationForm, UserEmailForm):
    state = ModelChoiceField(label=_("Bundesverband"),
                             queryset=State.objects.all())

    terms_and_conditions = BooleanField(label=u'Regeln des DBFV e.V./IFBB',
                                        help_text=u'Hiermit erkläre ich mich mit '
                                                  '<a href="/rules">'
                                                  'den Regeln</a> des DBFV e.V./IFBB einverstanden/',
                                        required=True)

    captcha = ReCaptchaField(attrs={'theme': 'clean'},
                             label=u'Sicherheitscheck',
                             help_text=u'Geben Sie bitte die Wörter ein, das dient als '
                                       u'Sicherheitsmaßname gegen Spam',)




class SubmissionStarterForm(ModelForm):

    CHAMPIONSHIPS = (
        # ('1', u'Deutsche Junioren und Masters am 18.04.2015 in Berlin'),
        # ('2', u'Int. Deutsche Newcomer-Meisterschaft am 25.04.2015 in Fulda/Petersberg'),
        # ('3', u'Deutsche Jugendmeisterschaft am 25.04.2015 in Fulda/Petersberg'),
        # ('4', u'NRW Landesmeisterschaften am 02.05.2015 in Duisburg-Rheinhausen'),
        # ('5', u'NRW Newcomerklasse für Männer am 02.05.2015 in Duisburg-Rheinhausen'),
        # ('6', u'33. Duisburger Stadtmeisterschaft am 02.05.2015 in Duisburg-Rheinhausen'),
        ('7', u'Int. NRW Meisterschaften am 19.11.2016 in Duisburg-Rheinhausen'),
        ('8', u'Int. NRW Newcomer-Wertung für Männer am 19.11.2016 in Duisburg-Rheinhausen'),
    )

    gym = ModelChoiceField(queryset=Gym.objects.filter(is_active=True),
                           label='Studio')

    championships = MultipleChoiceField(label='Meisterschaften',
                                        choices=CHAMPIONSHIPS,
                                        required=False)

    terms_and_conditions = BooleanField(label=u'Regeln des DBFV e.V./IFBB',
                                        help_text=u'Hiermit erkläre ich mich mit '
                                                  '<a href="/rules">'
                                                  'den Regeln</a> des DBFV e.V./IFBB einverstanden/',
                                        required=True)

    class Meta:
        model = SubmissionStarter
        exclude = ('submission_status',)


class SubmissionInternationalForm(ModelForm):

    gym = ModelChoiceField(queryset=Gym.objects.filter(is_active=True),
                           label='Studio')

    class Meta:
        model = SubmissionInternational
        exclude = ('submission_status',)


class SubmissionInternationalFormBV(ModelForm):

    class Meta:
        model = SubmissionInternational
        exclude = ('submission_status',)


class SubmissionStarterFormBV(ModelForm):
    class Meta:
        model = SubmissionStarter
        fields = ('submission_status', )


class SubmissionGymForm(ModelForm):
    class Meta:
        model = SubmissionGym
        exclude = ('submission_status',)


class SubmissionGymFormBV(ModelForm):
    class Meta:
        model = SubmissionGym
        fields = ('submission_status', )


class SubmissionJudgeForm(ModelForm):
    class Meta:
        model = SubmissionJudge
        exclude = ('submission_status',)


class SubmissionJudgeFormBV(ModelForm):
    class Meta:
        model = SubmissionJudge
        fields = ('submission_status', )
