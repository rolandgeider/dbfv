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

from championship.models import Participation
from submission.models import SubmissionStarter
from submission.views.generic_views import DbfvFormMixin


class ParticipationCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new participation for a championship
    '''

    model = Participation
    permission_required = 'championship.add_participation'

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:championship:view', kwargs={'pk': self.object.championship.pk})

    def form_valid(self, form):
        '''
        Set user and participation number
        '''
        submission = get_object_or_404(SubmissionStarter, pk=self.kwargs['submission_pk'])
        participation = Participation.objects.filter(championship=form.instance.championship)\
            .aggregate(Max('participation_nr'))
        if not participation['participation_nr__max']:
            max_participation = 1
        else:
            max_participation = participation['participation_nr__max'] + 1

        form.instance.submission = submission
        form.instance.participation_nr = max_participation
        return super(ParticipationCreateView, self).form_valid(form)


class ParticipationUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates a participation
    '''

    model = Participation
    permission_required = 'championship.change_participation'

    def get_success_url(self):
        '''
        Return to the championship page
        '''
        return reverse('championship:championship:view', kwargs={'pk': self.object.championship.pk})
