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

from django.conf.urls import patterns, url, include

from championship.views import championships
from championship.views import categories


# sub patterns for championships
patterns_championship = patterns('',

    url(r'^liste/alle$',
        championships.ChampionshipListView.as_view(),
        name='list'),
    url(r'^hinzufuegen$',
        championships.ChampionshipCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/anzeigen$',
        championships.ChampionshipDetailView.as_view(),
        name='view'),
    url(r'^(?P<pk>\d+)/bearbeiten$',
        championships.ChampionshipUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/loeschen$',
        championships.ChampionshipDeleteView.as_view(),
        name='delete'),
)

# sub patterns for categories
patterns_categories = patterns('',
    url(r'^hinzufuegen/meisterschaft-(?P<championship_pk>\d+)$',
        categories.CategoryCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/bearbeiten$',
        categories.CategoryUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/loeschen$',
        categories.CategoryDeleteView.as_view(),
        name='delete'),
)

urlpatterns = patterns('',
    url(r'^meisterschaft/', include(patterns_championship, namespace="championship")),
    url(r'^kategorie/', include(patterns_categories, namespace="category")),
)
