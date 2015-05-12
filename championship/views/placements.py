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

from django.db.models.aggregates import Max
from django.shortcuts import get_object_or_404
from django.views import generic
from django.core.urlresolvers import reverse

from championship.models import Participation, Placement, Category
from submission.models import SubmissionStarter
from submission.views.generic_views import DbfvFormMixin


class PlacementCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new placement for a participation in a championship
    '''

    model = Placement
    permission_required = 'championship.add_placement'

    def get_form(self, form_class):
        '''
        Only show categories for the current championship
        '''
        participation = get_object_or_404(Participation, pk=self.kwargs['participation_pk'])
        form = super(PlacementCreateView, self).get_form(form_class)
        form.fields['category'].queryset = \
            Category.objects.filter(championship=participation.championship)
        return form

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:participation:view',
                       kwargs={'pk': self.object.participation.pk})

    def form_valid(self, form):
        '''
        Set participation number
        '''
        participation = get_object_or_404(Participation, pk=self.kwargs['participation_pk'])
        form.instance.participation = participation
        return super(PlacementCreateView, self).form_valid(form)


class PlacementUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates a placement
    '''

    model = Placement
    permission_required = 'championship.change_placement'

    def get_form(self, form_class):
        '''
        Only show categories for the current championship
        '''
        form = super(PlacementUpdateView, self).get_form(form_class)
        form.fields['category'].queryset = \
            Category.objects.filter(championship=self.object.participation.championship)
        return form

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:participation:view',
                       kwargs={'pk': self.object.participation.pk})


class PlacementDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a placement
    '''

    model = Placement
    permission_required = 'championship.delete_placement'
    template_name = 'delete.html'

    def get_success_url(self):
        '''
        Return to the participation page
        '''
        return reverse('championship:participation:view',
                       kwargs={'pk': self.object.participation.pk})
