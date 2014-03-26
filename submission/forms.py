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

from django.forms import ModelForm
from django.forms import EmailField
from django.forms import ModelChoiceField
from django.contrib.auth.models import User as Django_User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _

from captcha.fields import ReCaptchaField

from submission.models import State


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
        raise ValidationError(_("This email is already used."))


class RegistrationForm(UserCreationForm, UserEmailForm):
    state = ModelChoiceField(label=_("Bundesverband"),
                             queryset=State.objects.all())
    captcha = ReCaptchaField(attrs={'theme': 'clean'},
                             label=_('Sicherheitscheck'),
                             help_text=u'Geben Sie bitte die Wörter ein, das dient als '
                                       u'Sicherheitsmaßname gegen Spam',)
