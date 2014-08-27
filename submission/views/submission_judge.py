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
import datetime

from django.views import generic
from django.core.urlresolvers import reverse_lazy

from submission.forms import SubmissionJudgeForm, SubmissionJudgeFormBV
from submission.models import SubmissionJudge
from submission.models import State
from submission.models import user_type
from submission.models import USER_TYPE_BUNDESVERBAND
from submission.models import USER_TYPE_USER
from submission.views.generic_views import DbfvViewMixin, BaseCsvExportView, BaseSubmissionListView
from submission.views.generic_views import BaseSubmissionDeleteView
from submission.views.generic_views import BaseSubmissionUpdateView
from submission.views.generic_views import DbfvFormMixin
from submission.views.generic_views import BaseSubmissionCreateView
from submission.views.generic_views import get_overview_context


class SubmissionListView(BaseSubmissionListView):
    '''
    Shows a list with all submissions
    '''

    model = SubmissionJudge
    template_name = 'submission/judge/list.html'

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all available dates
        '''
        context = super(SubmissionListView, self).get_context_data(**kwargs)

        queryset = SubmissionJudge.objects.all().order_by('state', 'creation_date')
        if user_type(self.request.user) == USER_TYPE_USER:
            queryset = queryset.filter(user=self.request.user)

        context.update(get_overview_context(self.model, queryset, self.request.user))
        return context


class SubmissionListMonthView(SubmissionListView,
                              generic.dates.MonthMixin,
                              generic.dates.YearMixin):
    permission_required = 'submission.change_submissionjudge'

    def get_queryset(self):
        '''
        Change the queryset depending on the user's rights. The rules are the
        following:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        '''

        queryset = SubmissionJudge.objects.filter(creation_date__month=self.get_month()) \
            .filter(creation_date__year=self.get_year()) \
            .order_by('gym__state', 'creation_date')
        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return queryset
        elif user_type(self.request.user) == USER_TYPE_USER:
            return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all available dates
        '''

        context = super(SubmissionListView, self).get_context_data(**kwargs)
        context['month_list'] = SubmissionJudge.objects.all().dates('creation_date', 'month')
        context['current_year'] = datetime.date.today().year
        context['current_month'] = datetime.date.today().month
        context['show_closed'] = True
        return context


class SubmissionDetailView(DbfvViewMixin, generic.detail.DetailView):
    login_required = True
    model = SubmissionJudge
    template_name = 'submission/judge/view.html'


class SubmissionCreateView(BaseSubmissionCreateView):
    '''
    Creates a new submissions
    '''

    model = SubmissionJudge
    form_class = SubmissionJudgeForm
    permission_required = 'submission.add_submissionjudge'
    page_title = 'Neue Kampfrichterlizenz beantragen'
    template_name = 'submission/judge/create.html'


class SubmissionDeleteView(BaseSubmissionDeleteView):
    '''
    Deletes a submission
    '''
    model = SubmissionJudge
    success_url = reverse_lazy('submission-judge-list')


class SubmissionUpdateView(BaseSubmissionUpdateView):
    '''
    Updates an existing submission
    '''
    model = SubmissionJudge
    form_class = SubmissionJudgeForm


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = SubmissionJudge
    form_class = SubmissionJudgeFormBV
    success_url = reverse_lazy('submission-judge-list')
    permission_required = 'submission.change_submissionjudge'
    page_title = 'Status bearbeiten'


class SubmissionCsvExportView(BaseCsvExportView):
    '''
    Exports all non-exported submissions to use for mail merge
    '''
    model = SubmissionJudge


class SubmissionCsvIndividualExportView(BaseCsvExportView):
    '''
    Exports an individual submission to use for mail merge
    '''

    model = SubmissionJudge
    update_submission_flag = False

    def get_submission_list(self):
        '''
        Return the current submission to export.
        '''
        return self.model.objects.filter(pk=self.kwargs['pk'])
