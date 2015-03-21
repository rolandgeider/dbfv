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

from django.views import generic
from django.core.urlresolvers import reverse_lazy
from championship.models import Championship

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
    success_url = reverse_lazy('championship:championship:list')
    permission_required = 'championship.add_championship'


class ChampionshipUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates a federal state
    '''

    model = Championship
    success_url = reverse_lazy('championship:championship:list')
    permission_required = 'championship.change_championship'


class ChampionshipDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a state
    '''

    model = Championship
    success_url = reverse_lazy('championship:championship:list')
    permission_required = 'submission.delete_championship'
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        '''
        Pass the title to the context
        '''
        context = super(ChampionshipDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Meisterschaft {0} löschen?'.format(self.object.name)
        return context
