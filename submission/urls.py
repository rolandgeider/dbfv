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
from django.core.urlresolvers import reverse_lazy
#from django.core.urlresolvers import reverse_lazy

from django.views.generic import TemplateView

from submission.views import gym
from submission.views import state
from submission.views import bank_account
from submission.views import submissions
from submission.views import user


urlpatterns = patterns('submission.views',

    # The index page
    url(r'^$',
        TemplateView.as_view(template_name="index.html"),
        name="index"),

    # User actions
    url(r'^benutzer/registrieren$', user.registration, name='registration'),
    url(r'^abmelden/$',
        'user.logout',
        name="logout"),
    url(r'^abmelden/ok$',
        TemplateView.as_view(template_name="user/logout.html"),
        name="logout-page"),


    # Gyms
    url(r'^studio/(?P<pk>\d+)/details/$',
        gym.GymDetailView.as_view(),
        name='gym-view'),
    url(r'^studio/liste/alle/$',
        gym.GymListView.as_view(),
        name='gym-list'),
    url(r'^studio/hinzufuegen/$',
        gym.GymCreateView.as_view(),
        name='gym-add'),
    url(r'^studio/(?P<pk>\d+)/bearbeiten/$',
        gym.GymUpdateView.as_view(),
        name="gym-edit"),

    # States
    url(r'^bundesland/liste/alle/$',
        state.StateListView.as_view(),
        name='state-list'),
    url(r'^bundesland/hinzufuegen/$',
        state.StateCreateView.as_view(),
        name='state-add'),
    url(r'^bundesland/(?P<pk>\d+)/bearbeiten/$',
        state.StateUpdateView.as_view(),
        name='state-edit'),

    # Bank account
    url(r'^bankkonto/liste/alle/$',
        bank_account.BankAccountListView.as_view(),
        name='bank-account-list'),
    url(r'^bankkonto/(?P<pk>\d+)/details/$',
        bank_account.BankAccountDetailView.as_view(),
        name='bank-account-view'),
    url(r'^bankkonto/hinzufuegen/$',
        bank_account.BankAccountCreateView.as_view(),
        name='bank-account-add'),
    url(r'^bankkonto/(?P<pk>\d+)/bearbeiten/$',
        bank_account.BankAccountUpdateView.as_view(),
        name='bank-account-edit'),

    # Submissions
    url(r'^antrag/liste/alle/$',
        submissions.SubmissionListView.as_view(),
        name='submission-list'),
    url(r'^antrag/liste/(?P<year>\d+)/$',
        submissions.SubmissionListYearView.as_view(),
        name='submission-list'),
    url(r'^antrag/stellen/(?P<type>(starterlizenz|kapmfrichterlizenz))$',
        submissions.SubmissionCreateView.as_view(),
        name='submission-add'),
    url(r'^antrag/(?P<pk>\d+)/bearbeiten/$',
        submissions.SubmissionUpdateView.as_view(),
        name='submission-edit'),
    url(r'^antrag/(?P<pk>\d+)/bearbeiten/status$',
        submissions.SubmissionUpdateStatusView.as_view(),
        name='submission-edit-status'),

    # Impressum
    url(r'^impressum$',
        TemplateView.as_view(template_name="misc/impressum.html"),
        name="impressum"),
    url(r'^kontakt$',
        TemplateView.as_view(template_name="misc/kontakt.html"),
        name="kontakt"),

)

# Password reset is implemented by Django, no need to cook our own soup here
# (besides the templates)
urlpatterns = urlpatterns + patterns('',
    url(r'^anmelden/$',
        'django.contrib.auth.views.login',
        {'template_name': 'user/login.html'},
        name='login'),

    url(r'^user/password/change$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'user/change_password.html',
          'post_change_redirect': reverse_lazy('index')},
        name='change-password'),

    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'template_name': 'user/password_reset_form.html'},
        name='password_reset'),

    url(r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'user/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^user/password/reset/check/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'user/password_reset_confirm.html'},
        name='password_reset_confirm'),

    url(r'^user/password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'user/password_reset_complete.html'},
        name='password_reset_complete'),
    )

from django.conf import settings
urlpatterns = urlpatterns + patterns('',
    (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
