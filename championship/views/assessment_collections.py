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
import csv

from django.core.urlresolvers import reverse
from django.http import HttpResponse
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


@permission_required('championship.add_assessmentcollection')
def add_collection(request, category_pk, championship_pk):
    '''
    Adds a collection to a category

    This view automatically checks the category type (2 or 3 rounds) and
    checks how many rounds have there been already. Except for the initial
    round where all participations are added, all further ones are filtered.
    '''
    championship = get_object_or_404(Championship, pk=championship_pk)
    category = get_object_or_404(Category, pk=category_pk)
    collection_list = AssessmentCollection.objects.filter(championship=championship,
                                                          category=category)
    collection = collection_list.first()
    results = collection.get_sorted_results()

    count = collection_list.count()
    round = count + 1

    #
    # First round
    # -> all categories are the same, just add all participations
    #
    if count == 0:
        participations = Participation.objects.filter(championship=championship)

    #
    # Half or Final round
    # -> select the top15 or top6 from the ranking of the previous round
    #
    elif count ==1:

        # Top 6 (finals)
        if category.category_type == '2':
            participations = [i['participation'] for i in results[:6]]
        # Top 15 (semi finals)
        elif category.category_type == '3':
            participations = [i['participation'] for i in results[:15]]

    elif count ==2:
        # Not possible, redirect
        if category.category_type == '2':
            return HttpResponseRedirect(reverse('championship:championship:category-detail',
                                        kwargs={'pk': championship.pk,
                                                'category_pk': category.pk}))
        # Top 6 (finals)
        if category.category_type == '3':
            participations = [i['participation'] for i in results[:6]]

    # No categories have more than 2 rounds, redirect
    else:
        return HttpResponseRedirect(reverse('championship:championship:category-detail',
                                            kwargs={'pk': championship.pk,
                                                    'category_pk': category.pk}))

    collection_list = AssessmentCollection(championship=championship,
                                           category=category,
                                           round=round)
    collection_list.save()
    for participation in participations:
        placement = participation.placement_set.filter(category=category)
        if placement:
            for judge in championship.judge_set.all():
                Assessment(collection=collection_list,
                           participation=participation,
                           judge=judge).save()
    HttpResponseRedirect(reverse('championship:championship:category-detail',
                                 kwargs={'pk': championship.pk,
                                         'category_pk': category.pk}))



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


@permission_required('championship.change_assessmentcollection')
def export_collection(request, pk):
    '''
    Export the a collection as a CSV
    '''

    collection = get_object_or_404(AssessmentCollection, pk=pk)
    results = collection.get_sorted_results()

    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    header = ['Nr', 'Name', ]
    for judge in collection.championship.judge_set.all():
        header.append(judge.name)
    header.append('Punkte')
    header.append('Platz')
    writer.writerow(header)

    for item in results:
        participation = item['participation']
        out = [participation.participation_nr,
               participation.submission.get_name,
               ]
        for placement in item['judges']:
            out.append(placement.points)
        out.append(item['points'])
        out.append(item['placement'])
        writer.writerow(out)

    # Send the data to the browser
    response['Content-Disposition'] = 'attachment; filename=Meisterschaft-{0}-Klasse-{1}-Runde-{2}.csv'.\
        format(collection.championship.pk,
               collection.category,
               collection.round)
    response['Content-Length'] = len(response.content)
    return response