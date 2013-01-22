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

from submission.models import State


class StateListView(generic.ListView):
    '''
    Shows a list with all federal states
    '''

    context_object_name = "state_list"
    model = State
    template_name = 'state/list.html'


class StateCreateView(generic.CreateView):
    '''
    Creates a new federal state
    '''

    model = State
    template_name = 'form.html'
    success_url = reverse_lazy('state-list')


class StateUpdateView(generic.UpdateView):
    '''
    Updates a federal state
    '''

    model = State
    template_name = 'form.html'
    success_url = reverse_lazy('state-list')
