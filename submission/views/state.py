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
# Django
from django.urls import reverse_lazy
from django.views import generic

# dbfv
from submission.models import State
from submission.views.generic_views import (
    DbfvFormMixin,
    DbfvViewMixin,
)


class StateListView(DbfvViewMixin, generic.ListView):
    """
    Shows a list with all federal states
    """

    model = State
    context_object_name = "state_list"
    template_name = 'state/list.html'
    permission_required = 'submission.add_state'
    login_required = True


class StateCreateView(DbfvFormMixin, generic.CreateView):
    """
    Creates a new federal state
    """

    model = State
    success_url = reverse_lazy('state-list')
    permission_required = 'submission.add_state'


class StateUpdateView(DbfvFormMixin, generic.UpdateView):
    """
    Updates a federal state
    """

    model = State
    fields = ['name', 'short_name', 'email', 'bank_account']
    success_url = reverse_lazy('state-list')
    permission_required = 'submission.change_state'


class StateDeleteView(DbfvFormMixin, generic.DeleteView):
    """
    Deletes a state
    """

    model = State
    success_url = reverse_lazy('state-list')
    permission_required = 'submission.delete_state'
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        """
        Pass the title to the context
        """
        context = super(StateDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Bundesland {0} löschen?'.format(self.object.name)
        context['delete_message'] = u'Das wird auch alle Anträge und Benutzer im ' \
                                    'Bundesland entfernen.'
        return context
