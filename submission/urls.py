# -*- coding: utf-8 *-*

# This file is part of Kumasta.
#
# Kumasta is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Kumasta is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from django.conf.urls import patterns, url
#from django.core.urlresolvers import reverse_lazy

from django.views.generic import TemplateView

from submission.views import gym
from submission.views import state
from submission.views import bank_account
from submission.views import submissions


urlpatterns = patterns('',

    # The index page
    url(r'^$',
        TemplateView.as_view(template_name="index.html"),
        name="index"),

    # Gyms
    url(r'^gym/(?P<pk>\d+)/view/$',
        gym.GymDetailView.as_view(),
        name='gym-view'),
    url(r'^gym/view/all/$',
        gym.GymListView.as_view(),
        name='gym-list'),
    url(r'^gym/add/$',
        gym.GymCreateView.as_view(),
        name='gym-add'),
    url(r'^gym/(?P<pk>\d+)/edit/$',
        gym.GymUpdateView.as_view(),
        name="gym-edit"),

    # States
    url(r'^state/view/all/$',
        state.StateListView.as_view(),
        name='state-list'),
    url(r'^state/add/$',
        state.StateCreateView.as_view(),
        name='state-add'),
    url(r'^state/(?P<pk>\d+)/edit/$',
        state.StateUpdateView.as_view(),
        name='state-edit'),

    # Bank account
    url(r'^bank-account/view/all/$',
        bank_account.BankAccountListView.as_view(),
        name='bank-account-list'),
    url(r'^bank-account/add/$',
        bank_account.BankAccountCreateView.as_view(),
        name='bank-account-add'),
    url(r'^bank-account/(?P<pk>\d+)/edit/$',
        bank_account.BankAccountUpdateView.as_view(),
        name='bank-account-edit'),

    # Submissions
    url(r'^submission/view/all/$',
        submissions.SubmissionListView.as_view(),
        name='submission-list'),
    url(r'^submission/add/$',
        submissions.SubmissionCreateView.as_view(),
        name='submission-add'),
    url(r'^submission/(?P<pk>\d+)/edit/$',
        submissions.SubmissionUpdateView.as_view(),
        name='submission-edit'),

)

# Password reset is implemented by Django, no need to cook our own soup here
# (besides the templates)
urlpatterns = urlpatterns + patterns('',
    url(r'^anmelden/$',
        'django.contrib.auth.views.login',
        {'template_name': 'user/login.html'},
        name='login'),

    url(r'^abmelden/$',
        'django.contrib.auth.views.logout',
        {'template_name': 'user/logout.html'},
        name='logout'),


#    url(r'^benutzer/passwort/aendern$',
#        'application.auth.views.password_change',
#        {'template_name': 'user/password_change.html',
#          'post_change_redirect': reverse_lazy('index'),
#          'password_change_form': PasswordChangeForm},
#        name='change-password'),

#    url(r'^benutzer/passwort/zuruecksetzen/$',
#        'application.auth.views.password_reset',
#        {'template_name': 'user/password_reset_form.html'},
#        name='password_reset'),

#    url(r'^benutzer/passwort/zuruecksetzen/ok/$',
#        'application.auth.views.password_reset_done',
#        {'template_name': 'user/password_reset_done.html'},
#        name='password_reset_done'),

#url(r'^benutzer/passwort/zuruecksetzen/pruefen/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
#        'application.auth.views.password_reset_confirm',
#        {'template_name': 'user/password_reset_confirm.html'},
#        name='password_reset_confirm'),

#    url(r'^benutzer/passwort/zuruecksetzen/erfolgt/$',
#        'application.auth.views.password_reset_complete',
#        {'template_name': 'user/password_reset_complete.html'},
#        name='password_reset_complete'),
    )
