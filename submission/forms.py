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
# Django
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User as Django_User
from django.core.exceptions import ValidationError
from django.forms import (
    BooleanField,
    EmailField,
    ModelChoiceField,
    ModelForm,
    MultipleChoiceField,
)
from django.utils.translation import gettext as _

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column


# dbfv
from submission.models import (
    Gym,
    State,
    SubmissionGym,
    SubmissionInternational,
    SubmissionJudge,
    SubmissionStarter, BankAccount,
)


class UserEmailForm(ModelForm):
    email = EmailField(
        label=_("Email"),
        required=True
    )

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
    state = ModelChoiceField(label=_("Bundesverband"), queryset=State.objects.all())

    email = EmailField(label="Email", required=True)

    terms_and_conditions = BooleanField(
        label='Regeln des DBFV e.V./IFBB',
        help_text='Hiermit erkläre ich mich mit den Regeln des DBFV e.V. IFBB einverstanden',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Anmelden', css_class='btn-success'))
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-12 mb-0'),
                Column('email', css_class='form-group col-12 mb-0'),
                Column('password1', css_class='form-group col-6 mb-0'),
                Column('password2', css_class='form-group col-6 mb-0'),
                Column('state', css_class='form-group col-12 mb-0'),
                Column('terms_and_conditions', css_class='form-group col-12 mb-0'),
                css_class='form-row'
            )
        )


    #captcha = ReCaptchaField(attrs={'theme': 'clean'},
    #                         label=u'Sicherheitscheck',
    #                         help_text=u'Geben Sie bitte die Wörter ein, das dient als '
    #                                   u'Sicherheitsmaßname gegen Spam',)


class SubmissionStarterForm(ModelForm):

    CHAMPIONSHIPS = (
        # ('1', u'Deutsche Junioren und Masters am 18.04.2015 in Berlin'),
        # ('2', u'Int. Deutsche Newcomer-Meisterschaft am 25.04.2015 in Fulda/Petersberg'),
        # ('3', u'Deutsche Jugendmeisterschaft am 25.04.2015 in Fulda/Petersberg'),
        # ('4', u'NRW Landesmeisterschaften am 02.05.2015 in Duisburg-Rheinhausen'),
        # ('5', u'NRW Newcomerklasse für Männer am 02.05.2015 in Duisburg-Rheinhausen'),
        # ('6', u'33. Duisburger Stadtmeisterschaft am 02.05.2015 in Duisburg-Rheinhausen'),
        # ('7', u'Int. NRW Meisterschaften am 19.11.2016 in Duisburg-Rheinhausen'),
        # ('8', u'Int. NRW Newcomer-Wertung für Männer am 19.11.2016 in Duisburg-Rheinhausen'),
        ('9', u'NRW Landesmeisterschaft am 06.05.2017 in Duisburg-Rheinhausen'),
        ('10', u'NRW Newcomer-Wertung für Männer am 06.05.2017 in Duisburg-Rheinhausen'),
    )

    gym = ModelChoiceField(queryset=Gym.objects.filter(is_active=True), label='Studio')

    championships = MultipleChoiceField(
        label='Meisterschaften', choices=CHAMPIONSHIPS, required=False
    )

    terms_and_conditions = BooleanField(
        label=u'Regeln des DBFV e.V./IFBB',
        help_text=u'Hiermit erkläre ich mich mit '
        '<a href="/rules">'
        'den Regeln</a> des DBFV e.V./IFBB einverstanden/',
        required=True
    )

    class Meta:
        model = SubmissionStarter
        exclude = ('submission_status', )


class SubmissionInternationalForm(ModelForm):

    gym = ModelChoiceField(queryset=Gym.objects.filter(is_active=True), label='Studio')

    class Meta:
        model = SubmissionInternational
        exclude = ('submission_status', )


class SubmissionInternationalFormBV(ModelForm):

    class Meta:
        model = SubmissionInternational
        exclude = ('submission_status', )


class SubmissionStarterFormBV(ModelForm):

    class Meta:
        model = SubmissionStarter
        fields = ('submission_status', )


class SubmissionGymForm(ModelForm):

    class Meta:
        model = SubmissionGym
        exclude = ('submission_status', )


class SubmissionGymFormBV(ModelForm):

    class Meta:
        model = SubmissionGym
        fields = ('submission_status', )


class SubmissionJudgeForm(ModelForm):

    class Meta:
        model = SubmissionJudge
        exclude = ('submission_status', )


class SubmissionJudgeFormBV(ModelForm):

    class Meta:
        model = SubmissionJudge
        fields = ('submission_status', )


class GymForm(ModelForm):
    """
    Gym form
    """

    class Meta:
        model = Gym
        fields = [
            'name',
            'email',
            'state',
            'owner',
            'zip_code',
            'city',
            'street',
            'is_active',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Speichern', css_class='btn-success'))
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-12 mb-0'),
                Column('email', css_class='form-group col-6 mb-0'),
                Column('state', css_class='form-group col-6 mb-0'),
                Column('owner', css_class='form-group col-12 mb-0'),
                Column('zip_code', css_class='form-group col-3 mb-0'),
                Column('city', css_class='form-group col-5 mb-0'),
                Column('street', css_class='form-group col-4 mb-0'),
                Column('is_active', css_class='form-group col-6 mb-0'),
                css_class='form-row'
            )
        )


class StateForm(ModelForm):
    """
    Form for a state
    """

    class Meta:
        model = State
        fields = [
            'name',
            'short_name',
            'email',
            'bank_account'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Speichern', css_class='btn-success'))
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-6 mb-0'),
                Column('short_name', css_class='form-group col-6 mb-0'),
                Column('email', css_class='form-group col-12 mb-0'),
                Column('bank_account', css_class='form-group col-12 mb-0'),
                css_class='form-row'
            )
        )


class BankAccountForm(ModelForm):
    """
    Form for a bank account
    """

    class Meta:
        model = BankAccount
        fields = [
            'owner_name',
            'iban',
            'bic',
            'bank_name'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Speichern', css_class='btn-success'))
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Row(
                Column('bank_name', css_class='form-group col-12 mb-0'),
                Column('owner_name', css_class='form-group col-12 mb-0'),
                Column('iban', css_class='form-group col-6 mb-0'),
                Column('bic', css_class='form-group col-6 mb-0'),
                css_class='form-row'
            )
        )


class DbfvAuthenticationForm(AuthenticationForm):
    """
    Form used for logging in to the DBFV application
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Anmelden', css_class='btn-success'))
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-12 mb-0'),
                Column('password', css_class='form-group col-12 mb-0'),
                css_class='form-row'
            )
        )


class DbfvPasswordResetForm(PasswordResetForm):
    """
    Form used to reset a password
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Abschicken', css_class='btn-success'))
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='form-group col-12 mb-0'),
                css_class='form-row'
            )
        )