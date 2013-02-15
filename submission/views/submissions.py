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
from django.forms import ModelForm

from submission.models import Submission
from submission.models import SUBMISSION_STATUS_EINGEGANGEN
from submission.models import SUBMISSION_STATUS_BEWILLIGT
from submission.models import SUBMISSION_TYPES

from submission.views.generic_views import DbfvViewMixin
from submission.views.generic_views import DbfvFormMixin


class SubmissionListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all submissions
    '''

    model = Submission
    context_object_name = "submission_list"
    template_name = 'submission/list.html'
    login_required = True


class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        exclude = ('user',
                   'submission_status_lv',
                   'submission_status_bv',
                   'submission_type')


class SubmissionCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new submissions
    '''

    model = Submission
    form_class = SubmissionForm
    success_url = reverse_lazy('index')
    permission_required = 'submission.add_submission'

    def form_valid(self, form):
        '''
        Manually set the user when saving the form
        '''
        form.instance.user = self.request.user
        form.instance.submission_status = SUBMISSION_STATUS_EINGEGANGEN

        # Starterlizenz
        if self.kwargs['type'] == SUBMISSION_TYPES[0][1]:
            form.instance.submission_type = SUBMISSION_TYPES[0][0]
            print form.instance.submission_type

        # Kampfrichter
        else:
            form.instance.submission_type = SUBMISSION_TYPES[1][0]
            print form.instance.submission_type

        return super(SubmissionCreateView, self).form_valid(form)


class SubmissionUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = Submission
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submission'
