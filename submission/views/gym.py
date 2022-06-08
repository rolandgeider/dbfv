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
from django.urls import reverse_lazy
from django.views import generic


from submission.models import Gym, State
from submission.views.generic_views import DbfvViewMixin
from submission.views.generic_views import DbfvFormMixin


class GymListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all gyms
    '''

    context_object_name = "gym_list"
    model = Gym
    template_name = 'gym/list.html'
    permission_required = 'submission.change_gym'

    def get_queryset(self):
        '''
        Filter by state
        '''
        return Gym.objects.filter(state=self.kwargs['state_pk'])

    def get_context_data(self, **kwargs):
        '''
        Pass the state to the context
        '''
        context = super(GymListView, self).get_context_data(**kwargs)
        context['state'] = State.objects.get(pk=self.kwargs['state_pk'])
        return context


class GymDetailView(DbfvViewMixin, generic.DetailView):
    '''
    Detail view of a gym
    '''

    model = Gym
    template_name = 'gym/view.html'
    permission_required = 'submission.change_gym'


class GymCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Shows a list with all konzepts
    '''

    model = Gym
    permission_required = 'submission.add_gym'
    page_title = 'Studio hinzufügen'
    fields = '__all__' 


class GymUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Edits an existing Gym
    '''

    model = Gym
    permission_required = 'submission.change_gym'
    page_title = 'Studio bearbeiten'
    fields = '__all__' 


class GymDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a gym
    '''

    model = Gym
    success_url = reverse_lazy('gym-list')
    permission_required = 'submission.delete_gym'
    template_name = 'delete.html'
    fields = '__all__' 

    def get_context_data(self, **kwargs):
        '''
        Pass the title to the context
        '''
        context = super(GymDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Studio {0} löschen?'.format(self.object.name)
        context['delete_message'] = u'Das wird auch alle Anträge zu diesem Studio entfernen.'
        return context
