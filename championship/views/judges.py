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
from django.shortcuts import get_object_or_404

from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from championship.models import (
    Judge,
    Championship,
    judge_fields,
)

from submission.views.generic_views import DbfvViewMixin, DbfvFormMixin


class JudgeCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new federal state
    '''

    model = Judge
    fields = judge_fields
    permission_required = 'championship.add_judge'

    def form_valid(self, form):
        '''
        Set participation number
        '''
        championship = get_object_or_404(Championship, pk=self.kwargs['championship_pk'])
        form.instance.championship = championship
        return super(JudgeCreateView, self).form_valid(form)

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:championship:view',
                       kwargs={'pk': self.kwargs['championship_pk']})


class JudgeUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates a federal state
    '''

    model = Judge
    fields = judge_fields
    permission_required = 'championship.change_judge'

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:championship:view', kwargs={'pk': self.object.championship_id})


class JudgeDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a state
    '''

    model = Judge
    fields = judge_fields
    permission_required = 'championship.delete_judge'
    template_name = 'delete.html'

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:championship:view', kwargs={'pk': self.object.championship_id})

    def get_context_data(self, **kwargs):
        '''
        Pass the title to the context
        '''
        context = super(JudgeDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Kampfrichter {0} löschen?'.format(self.object.name)
        return context

