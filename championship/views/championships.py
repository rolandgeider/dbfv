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
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from championship.models import (
    Championship,
    Category,
    championship_fields,
    Placement)

from submission.views.generic_views import DbfvViewMixin, DbfvFormMixin


class ChampionshipListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all federal states
    '''

    model = Championship
    context_object_name = "championship_list"
    template_name = 'championship/list.html'
    permission_required = 'championship.add_championship'
    login_required = True


class ChampionshipDetailView(DbfvFormMixin, generic.detail.DetailView):
    '''
    Details of a championship
    '''

    model = Championship
    permission_required = 'championship.change_championship'
    login_required = True
    template_name = 'championship/view.html'


class ChampionshipCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new federal state
    '''

    model = Championship
    fields = championship_fields
    permission_required = 'championship.add_championship'

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:championship:view', kwargs={'pk': self.object.pk})


class ChampionshipUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates a federal state
    '''

    model = Championship
    fields = championship_fields
    permission_required = 'championship.change_championship'

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:championship:view', kwargs={'pk': self.object.pk})


class ChampionshipDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a state
    '''

    model = Championship
    fields = championship_fields
    success_url = reverse_lazy('championship:championship:list')
    permission_required = 'championship.delete_championship'
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        '''
        Pass the title to the context
        '''
        context = super(ChampionshipDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Meisterschaft {0} löschen?'.format(self.object.name)
        return context


@permission_required('championship.change_championship')
def export_participants(request, pk):
    '''
    Export all participants for a championship
    '''

    championship = get_object_or_404(Championship, pk=pk)
    participants = championship.participation_set.all()

    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Teilnehmernr', 'Platzierung', 'Kategorie', 'Teilnehmer', 'Studio'])

    for participant in participants:
        for placement in participant.placement_set.all():
            writer.writerow([participant.participation_nr,
                             placement.placement,
                             placement.category,
                             participant.submission.get_name,
                             participant.submission.gym.name,
                             ])

    # Send the data to the browser
    response['Content-Disposition'] = 'attachment; filename=Meisterschaft-{0}.csv'.\
        format(championship.pk)
    response['Content-Length'] = len(response.content)
    return response


@permission_required('championship.change_championship')
def category_detail(request, pk, category_pk):
    '''
    View participations and other details for a category
    '''

    championship = get_object_or_404(Championship, pk=pk)
    category = get_object_or_404(Category, pk=pk)

    placements = Placement.objects.filter(participation__championship=championship,
                                          category=category,
                                          placement__gt=0)

    # participants = championship.participation_set.filter(category=category, placement__category=category)

    context = {'championship': championship,
               'category': category,
               'placements': placements}

    return render(request, 'championship/category_list.html', context)