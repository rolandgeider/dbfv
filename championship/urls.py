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

from django.conf.urls import url, include

from championship.views import (
    championships,
    categories,
    participations,
    placements,
    judges,
    assessment_collections,
)


# sub patterns for championships
patterns_championship = [

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
    url(r'^(?P<pk>\d+)/export-csv',
        championships.export_participants,
        name='export-csv'),
    url(r'^(?P<pk>\d+)/(?P<category_pk>\d+)/view',
        championships.category_detail,
        name='category-detail'),
]

# sub patterns for judges
patterns_judge = [
    url(r'^(?P<championship_pk>\d+)/hinzufuegen$',
        judges.JudgeCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/bearbeiten$',
        judges.JudgeUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/loeschen$',
        judges.JudgeDeleteView.as_view(),
        name='delete'),
]

# sub patterns for categories
patterns_categories = [
    url(r'^liste$',
        categories.CategoriesListView.as_view(),
        name='list'),
    url(r'^hinzufuegen$',
        categories.CategoryCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/bearbeiten$',
        categories.CategoryUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/loeschen$',
        categories.CategoryDeleteView.as_view(),
        name='delete'),
]

# sub patterns for participations
patterns_participation = [
  url(r'^(?P<pk>\d+)/loeschen$',
      participations.ParticipationDeleteView.as_view(),
      name='delete'),
  url(r'^(?P<pk>\d+)/anzeigen$',
      participations.ParticipationDetailView.as_view(),
      name='view'),
  url(r'^antrag-(?P<submission_pk>\d+)/anmelden$',  #JS!
      participations.ParticipationCreateView.as_view(),
      name='register'),
]

# sub patterns for championship placements
patterns_placement = [
  url(r'^(?P<pk>\d+)/bearbeiten$',
      placements.PlacementUpdateView.as_view(),
      name='edit'),
  url(r'^(?P<pk>\d+)/loeschen$',
      placements.PlacementDeleteView.as_view(),
      name='delete'),
  url(r'^antrag-(?P<participation_pk>\d+)/anmelden$',
      placements.PlacementCreateView.as_view(),
      name='register'),
]

# sub patterns for assessment collections
patterns_assessmentcollection = [
  url(r'^(?P<championship_pk>\d+)/(?P<category_pk>\d+)/erstellen',
      assessment_collections.add_collection,
      name='add'),
  url(r'^(?P<pk>\d+)/loeschen',
      assessment_collections.AssessmentCollectionDeleteView.as_view(),
      name='delete'),
  url(r'^(?P<pk>\d+)/fuer-endwertung-nutzen',
      assessment_collections.use_collection,
      name='use'),
  url(r'^(?P<pk>\d+)/editieren',
      assessment_collections.edit_collection,
      name='edit'),
  url(r'^(?P<pk>\d+)/export-csv',
      assessment_collections.export_collection,
      name='export-csv'),
]

urlpatterns = [
    url(r'^', include(patterns_championship, namespace="championship")),
    url(r'^teilnahme/', include(patterns_participation, namespace="participation")),
    url(r'^platzierung/', include(patterns_placement, namespace="placement")),
    url(r'^kategorie/', include(patterns_categories, namespace="category")),
    url(r'^kampfrichter/', include(patterns_judge, namespace="judge")),
    url(r'^wahlgaenge/', include(patterns_assessmentcollection, namespace="assessment-collection")),
]
