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

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import generic

from django.contrib.auth.decorators import permission_required

from submission.views.generic_views import DbfvFormMixin
from championship.models import (
    Participation,
    AssessmentCollection,
    Category,
    assessmentcollection_fields,
    Championship, Assessment, Placement)


class AssessmentCollectionCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a assessment collection and combinations for assessments and judges
    '''

    model = AssessmentCollection
    fields = assessmentcollection_fields
    permission_required = 'championship.add_assessmentcollection'

    def get_success_url(self):
        '''
        Return to the championship page and generate combinations for individual
        assessments

        It's a bit ugly to create objects here, but in form_valid the assessment
        collection is not saved yet.
        '''

        category = self.object.category
        participations = Participation.objects.filter(championship=self.object.championship)
        for participation in participations:
            placement = participation.placement_set.filter(category=category)
            if placement:
                for judge in self.object.championship.judge_set.all():
                    Assessment(collection=self.object,
                               participation=participation,
                               judge=judge).save()
        return reverse('championship:championship:category-detail',
                       kwargs={'pk': self.object.championship.pk,
                               'category_pk': self.object.category.pk})

    def form_valid(self, form):
        '''
        Set championship
        '''
        championship = get_object_or_404(Championship, pk=self.kwargs['championship_pk'])
        category = get_object_or_404(Category, pk=self.kwargs['category_pk'])
        form.instance.championship = championship
        form.instance.category = category
        return super(AssessmentCollectionCreateView, self).form_valid(form)


@permission_required('championship.change_assessmentcollection')
def use_collection(request, pk):
    '''
    Uses the given collection to calculate the final placements for the athletes
    '''
    collection = get_object_or_404(AssessmentCollection, pk=pk)
    results = collection.calculate_points()
    for participation in results:
        placement = Placement.objects.get(participation=participation,
                                          category=collection.category)
        placement.placement = results[participation]['placement']
        placement.points = results[participation]['points']
        placement.save()

    return HttpResponseRedirect((reverse('championship:championship:category-detail',
                                         kwargs={'pk': collection.championship.pk,
                                                 'category_pk': collection.category.pk})))

class AssessmentCollectionDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes an assessment collection
    '''

    model = AssessmentCollection
    fields = assessmentcollection_fields
    permission_required = 'championship.delete_assessmentcollection'
    template_name = 'delete.html'

    def get_success_url(self):
        '''
        Return to the participation page
        '''
        return reverse('championship:championship:category-detail',
                       kwargs={'pk': self.object.championship.pk,
                               'category_pk': self.object.category.pk})
