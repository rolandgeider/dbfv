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

from submission.views.gym import GymDetailView
from submission.views.gym import GymListView
from submission.views.gym import GymCreateView
from submission.views.gym import GymUpdateView

from submission.views.state import StateListView
from submission.views.state import StateCreateView
from submission.views.state import StateUpdateView

from submission.views.bank_account import BankAccountCreateView
from submission.views.bank_account import BankAccountUpdateView
from submission.views.bank_account import BankAccountListView


urlpatterns = patterns('',

    # The index page
    url(r'^$',
        TemplateView.as_view(template_name="index.html"),
        name="index"),

    # Gyms
    url(r'^gym/(?P<pk>\d+)/view/$',
        GymDetailView.as_view(),
        name='gym-view'),
    url(r'^gym/view/all/$',
        GymListView.as_view(),
        name='gym-list'),
    url(r'^gym/add/$',
        GymCreateView.as_view(),
        name='gym-add'),
    url(r'^gym/(?P<pk>\d+)/edit/$',
        GymUpdateView.as_view(),
        name="gym-edit"),

    # States
    url(r'^state/view/all/$',
        StateListView.as_view(),
        name='state-list'),
    url(r'^state/add/$',
        StateCreateView.as_view(),
        name='state-add'),
    url(r'^state/(?P<pk>\d+)/edit/$',
        StateUpdateView.as_view(),
        name='state-edit'),

    # Bank account
    url(r'^bank-account/view/all/$',
        BankAccountListView.as_view(),
        name='bank-account-list'),
    url(r'^bank-account/add/$',
        BankAccountCreateView.as_view(),
        name='bank-account-add'),
    url(r'^bank-account/(?P<pk>\d+)/edit/$',
        BankAccountUpdateView.as_view(),
        name='bank-account-edit'),



)
