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

from submission.views import GymDetailView
from submission.views import GymListView
from submission.views import GymCreateView
from submission.views import GymUpdateView

from submission.views import StateListView
from submission.views import StateCreateView


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

)
