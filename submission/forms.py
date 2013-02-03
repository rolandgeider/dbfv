

from django.forms import ModelForm
from django.forms import EmailField
from django.contrib.auth.models import User as Django_User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext as _

from captcha.fields import ReCaptchaField


class UserEmailForm(ModelForm):
    email = EmailField(label=_("Email"),
                       help_text=_("Completely optional, but needed to reset your password "
                                   "in case you forget it."),
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
    captcha = ReCaptchaField(attrs={'theme': 'clean'},
                             label=_('Confirmation text'),
                             help_text=_('As a security measure, please enter the previous words'),)
