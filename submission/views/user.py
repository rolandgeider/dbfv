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
from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.models import (
    Group,
    User as Django_User,
)
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import RequestContext, loader
from django.template.context_processors import csrf
from django.urls import reverse

# Third Party
from django_email_verification import send_email

# dbfv
from submission.forms import RegistrationForm
from submission.models import USER_TYPE_USER


def logout(request):
    """
    Logout the user
    """
    django_logout(request)
    return HttpResponseRedirect(reverse('logout-page'))


def registration(request):
    """
    A form to allow for registration of new users
    """

    context = {}
    context.update(csrf(request))

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)

        # If the data is valid, log in and redirect
        if form.is_valid():
            # Create the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            user = Django_User.objects.create_user(username, email, password)
            user.save()

            # New users are added to the 'User' group
            g = Group.objects.get(name='User')
            g.user_set.add(user)

            # Set the user type in the profile
            profile = user.userprofile
            profile.type = USER_TYPE_USER
            profile.state = form.cleaned_data['state']
            profile.save()

            # Login the new user and redirect
            user = authenticate(username=username, password=password)
            send_email(user)
            django_login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = RegistrationForm()

    context['form'] = form

    template = loader.get_template('form.html')
    return HttpResponse(template.render(context, request))
