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
import json

from django.http.response import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q

from submission.forms import SubmissionInternationalForm, SubmissionInternationalFormBV
from submission.models import SubmissionInternational
from submission.models import State
from submission.models import user_type
from submission.models import USER_TYPE_BUNDESVERBAND
from submission.models import USER_TYPE_USER
from submission.views.generic_views import DbfvViewMixin, BaseCsvExportView, BaseSubmissionListView
from submission.views.generic_views import BaseSubmissionCreateView
from submission.views.generic_views import BaseSubmissionDeleteView
from submission.views.generic_views import BaseSubmissionUpdateView
from submission.views.generic_views import DbfvFormMixin
from submission.views.generic_views import get_overview_context


class SubmissionListView(BaseSubmissionListView):
    """
    Shows a list with all submissions
    """

    model = SubmissionInternational
    template_name = 'submission/international/list.html'

    def get_context_data(self, **kwargs):
        """
        Pass a list of all available dates
        """
        context = super(SubmissionListView, self).get_context_data(**kwargs)

        queryset = SubmissionInternational.objects.all().order_by('gym__state', 'creation_date')
        if user_type(self.request.user) == USER_TYPE_USER:
            queryset = queryset.filter(user=self.request.user)

        context.update(get_overview_context(self.model, queryset, self.request.user))
        return context


class SubmissionListMonthView(
    SubmissionListView, generic.dates.MonthMixin, generic.dates.YearMixin
):
    permission_required = 'submission.change_submissioninternational'

    def get_queryset(self):
        """
        Change the queryset depending on the user's rights. The rules are the
        following:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        """

        queryset = SubmissionInternational.objects.filter(creation_date__month=self.get_month()) \
            .filter(creation_date__year=self.get_year()) \
            .order_by('gym__state', 'creation_date')
        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return queryset
        elif user_type(self.request.user) == USER_TYPE_USER:
            return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Pass a list of all available dates
        """

        context = super(SubmissionListView, self).get_context_data(**kwargs)

        # Count how many submissions were exported for each month
        month_list = []
        for date_obj in SubmissionInternational.objects.all().dates('creation_date', 'month'):
            tmp_count = SubmissionInternational.objects.filter(mail_merge=True)\
                                                 .filter(creation_date__month=date_obj.month)\
                                                 .filter(creation_date__year=date_obj.year)
            month_list.append({'date': date_obj, 'export_count': tmp_count.count()})
        context['submission_list'] = self.get_queryset()
        context['month_list'] = month_list
        context['current_year'] = datetime.date.today().year
        context['current_month'] = datetime.date.today().month
        context['show_closed'] = True
        return context


class SubmissionDetailView(DbfvViewMixin, generic.detail.DetailView):
    """
    Show the detail view of a submission
    """
    login_required = True
    model = SubmissionInternational
    template_name = 'submission/international/view.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Check for necessary permissions
        """
        submission = self.get_object()
        if not request.user.has_perm('submission.delete_submissioninternational') \
           and submission.user != request.user:
            return HttpResponseForbidden()

        # Save submission data to the session
        self.request.session['bank-account'] = submission.get_bank_account()
        self.request.session['submission-fee'] = SubmissionInternational.FEE
        self.request.session['designated-use'] = submission.get_bank_designated_use()
        return super(SubmissionDetailView, self).dispatch(request, *args, **kwargs)


class SubmissionCreateView(BaseSubmissionCreateView):
    """
    Creates a new submission
    """

    model = SubmissionInternational
    form_class = SubmissionInternationalForm
    permission_required = 'submission.add_submissioninternational'
    template_name = 'submission/international/create.html'

    def get_context_data(self, **kwargs):
        """
        Pass a list of all states
        """
        context = super(SubmissionCreateView, self).get_context_data(**kwargs)
        context['states_list'] = State.objects.all()
        return context


class SubmissionDeleteView(BaseSubmissionDeleteView):
    """
    Deletes a submission
    """
    model = SubmissionInternational
    success_url = reverse_lazy('submission-list')


class SubmissionUpdateView(BaseSubmissionUpdateView):
    """
    Updates an existing submission
    """
    model = SubmissionInternational
    form_class = SubmissionInternationalForm


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    """
    Updates an existing submissions
    """

    model = SubmissionInternational
    form_class = SubmissionInternationalFormBV
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submissioninternational'


class SubmissionCsvExportView(BaseCsvExportView):
    """
    Exports all non-exported submissions to use for mail merge
    """
    model = SubmissionInternational


class SubmissionCsvIndividualExportView(BaseCsvExportView):
    """
    Exports an individual submission to use for mail merge
    """

    model = SubmissionInternational
    update_submission_flag = False

    def get_submission_list(self):
        """
        Return the current submission to export.
        """
        return self.model.objects.filter(pk=self.kwargs['pk'])


def search(request):
    """
    Search for a submission, return the result as a JSON list
    """
    if not request.user.has_perm('submission.change_submissioninternational'):
        return HttpResponseForbidden()

    # Perform the search
    q = request.GET.get('q', '')

    if q:
        submissions = (
            SubmissionInternational.objects.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(gym__name__icontains=q)
            ).distinct()
        )
        results = []
        for submission in submissions[:30]:
            results.append(submission.get_search_json())
        data = json.dumps(results)

    else:
        data = []

    return HttpResponse(data, content_type='application/json')
