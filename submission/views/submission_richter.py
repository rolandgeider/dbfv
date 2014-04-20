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
from submission.views.generic_views import DbfvViewMixin
from submission.views.generic_views import DbfvFormMixin


class SubmissionListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all submissions
    '''

    model = SubmissionJudge
    context_object_name = "submission_list"
    template_name = 'submission/judge/list.html'
    login_required = True

    def get_queryset(self):
        '''
        Change the queryset depending on the user's rights. The rules are the
        following:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        '''

        queryset = SubmissionJudge.objects.all().order_by('state', 'creation_date')

        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return queryset
        elif user_type(self.request.user) == USER_TYPE_USER:
            return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all available dates
        '''
        year = datetime.date.today().year
        month = datetime.date.today().month

        context = super(SubmissionListView, self).get_context_data(**kwargs)
        context['month_list'] = self.get_queryset().dates('creation_date', 'month')
        context['current_year'] = year
        context['current_month'] = month
        context['show_closed'] = False if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND \
            else True
        context['mailmerge_count'] = SubmissionJudge.objects\
            .filter(submission_status=SubmissionJudge.SUBMISSION_STATUS_BEWILLIGT) \
            .count()
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


class SubmissionCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new submissions
    '''

    model = SubmissionJudge
    form_class = SubmissionJudgeForm
    success_url = reverse_lazy('index')
    permission_required = 'submission.add_submissionjudge'
    page_title = 'Neue Kampfrichterlizenz beantragen'
    template_name = 'submission/judge/create.html'

    def form_valid(self, form):
        '''
        Manually set the user when saving the form
        '''

        form.instance.user = self.request.user
        self.form_instance = form.instance

        # Notify the administrators
        form.instance.send_emails()
        return super(SubmissionCreateView, self).form_valid(form)

    def get_success_url(self):
        '''
        Redirect to bank acount page
        '''

        self.request.session['bank-account'] = self.form_instance.state.bank_account_id
        self.request.session['submission-fee'] = SubmissionJudge.FEE
        self.request.session['designated-use'] = 'Kampfrichterlizenz {0}<br>\n{1}'.format(self.object.pk,
                                                                                          self.object.get_name)
        return reverse_lazy('bank-account-view')

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all states
        '''
        context = super(SubmissionCreateView, self).get_context_data(**kwargs)
        context['states_list'] = State.objects.all()
        context['fee'] = SubmissionJudge.FEE
        return context


class SubmissionDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a submission
    '''

    model = SubmissionJudge
    success_url = reverse_lazy('submission-judge-list')
    permission_required = 'submission.delete_submissionjudge'
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        '''
        Pass the title to the context
        '''
        context = super(SubmissionDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Antrag {0} löschen?'.format(self.object.id)
        return context


class SubmissionUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = SubmissionJudge
    #success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submissionjudge'


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = SubmissionJudge
    form_class = SubmissionJudgeFormBV
    success_url = reverse_lazy('submission-judge-list')
    permission_required = 'submission.change_submissionjudge'
    page_title = 'Status bearbeiten'
