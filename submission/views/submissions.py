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
import datetime

from django.http.response import HttpResponse, HttpResponseForbidden
from django.views import generic
from django.core.urlresolvers import reverse_lazy

from submission.forms import SubmissionStarterForm, SubmissionStarterFormBV
from submission.helpers import export_submission_mailmerge
from submission.helpers import MAILMERGE_HEADER
from submission.models import SubmissionStarter
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

    model = SubmissionStarter
    context_object_name = "submission_list"
    template_name = 'submission/list.html'
    login_required = True

    def get_queryset(self):
        '''
        Change the queryset depending on the user's rights. The rules are the
        following:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        '''

        queryset = SubmissionStarter.objects.all().order_by('gym__state', 'creation_date')

        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return queryset
        elif user_type(self.request.user) == USER_TYPE_USER:
            return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all available dates
        '''
        context = super(SubmissionListView, self).get_context_data(**kwargs)

        # Count how many submissions were exported for each month
        month_list = []
        for date_obj in self.get_queryset().dates('creation_date', 'month'):
            tmp_count = SubmissionStarter.objects.filter(mail_merge=True)\
                                                 .filter(creation_date__month=date_obj.month)\
                                                 .filter(creation_date__year=date_obj.year)

            month_list.append({'date': date_obj,
                               'export_count': tmp_count.count()})
        context['month_list'] = month_list
        context['current_year'] = datetime.date.today().year
        context['current_month'] = datetime.date.today().month
        context['show_closed'] = False if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND \
            else True
        context['mailmerge_count'] = SubmissionStarter.objects.filter(mail_merge=False) \
            .filter(submission_status=SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT) \
            .count()
        return context


class SubmissionListMonthView(SubmissionListView,
                              generic.dates.MonthMixin,
                              generic.dates.YearMixin):
    permission_required = 'submission.change_submissionstarter'

    def get_queryset(self):
        '''
        Change the queryset depending on the user's rights. The rules are the
        following:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        '''

        queryset = SubmissionStarter.objects.filter(creation_date__month=self.get_month()) \
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

        # Count how many submissions were exported for each month
        month_list = []
        for date_obj in SubmissionStarter.objects.all().dates('creation_date', 'month'):
            tmp_count = SubmissionStarter.objects.filter(mail_merge=True)\
                                                 .filter(creation_date__month=date_obj.month)\
                                                 .filter(creation_date__year=date_obj.year)
            month_list.append({'date': date_obj,
                               'export_count': tmp_count.count()})
        context['month_list'] = month_list
        context['current_year'] = datetime.date.today().year
        context['current_month'] = datetime.date.today().month
        context['show_closed'] = True
        return context


class SubmissionDetailView(DbfvViewMixin, generic.detail.DetailView):
    login_required = True
    model = SubmissionStarter

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for necessary permissions
        '''
        submission = self.get_object()
        if not request.user.has_perm('submission.delete_submissionstarter') \
            and submission.user != request.user:
            return HttpResponseForbidden()

        # Save submission data to the session
        self.request.session['bank-account'] = submission.get_bank_account()
        self.request.session['submission-fee'] = SubmissionStarter.FEE
        self.request.session['designated-use'] = u'Starterlizenz {0}<br>\n{1}'.format(submission.pk,
                                                                                      submission.get_name)
        return super(SubmissionDetailView, self).dispatch(request, *args, **kwargs)


class SubmissionCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new submissions
    '''

    model = SubmissionStarter
    form_class = SubmissionStarterForm
    permission_required = 'submission.add_submissionstarter'
    template_name = 'submission/starter/create.html'

    def form_valid(self, form):
        '''
        Manually set the user when saving the form
        '''

        form.instance.user = self.request.user
        self.form_instance = form.instance

        return super(SubmissionCreateView, self).form_valid(form)

    def get_success_url(self):
        '''
        Redirect to bank account page and send appropriate emails
        '''
        self.form_instance.send_emails()

        self.request.session['bank-account'] = self.form_instance.get_bank_account()
        self.request.session['submission-fee'] = SubmissionStarter.FEE
        self.request.session['designated-use'] = u'Starterlizenz {0}<br>\n{1}'.format(self.object.pk,
                                                                                      self.object.get_name)
        return reverse_lazy('bank-account-view')

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all states
        '''
        context = super(SubmissionCreateView, self).get_context_data(**kwargs)
        context['states_list'] = State.objects.all()
        context['fee'] = SubmissionStarter.FEE
        return context

    def get_initial(self):
        '''
        Fill in some data
        '''
        return {'email': self.request.user.email}


class SubmissionDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a submission
    '''

    model = SubmissionStarter
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.delete_submissionstarter'
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
    Updates an exsiting submission

    The owner user can update his own submission while it is still in the
    pending state. Once it has been accepted, only the BV can edit it.
    '''

    model = SubmissionStarter
    form_class = SubmissionStarterForm
    login_required = True
    page_title = 'Antrag bearbeiten'

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for necessary permissions
        '''
        submission = self.get_object()
        if not request.user.has_perm('submission.delete_submissionstarter') \
            and (submission.submission_status != SubmissionStarter.SUBMISSION_STATUS_EINGEGANGEN
                 or submission.user != request.user):
            return HttpResponseForbidden(u'Sie dürfen dieses Objekt nicht editieren!')

        return super(SubmissionUpdateView, self).dispatch(request, *args, **kwargs)


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = SubmissionStarter
    form_class = SubmissionStarterFormBV
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submissionstarter'


def export_csv(request, pk):
    '''
    Exports a submission as a CSV file to be imported into an office application
    '''
    if not request.user.has_perm('submission.change_submissionstarter'):
        return HttpResponseForbidden()

    response = HttpResponse(mimetype='text/csv')
    writer = csv.writer(response, delimiter='\t')
    today = datetime.date.today()

    submission = SubmissionStarter.objects.filter(pk=pk)

    # Write the CSV file
    writer.writerow(MAILMERGE_HEADER)
    for line in export_submission_mailmerge(submission):
        writer.writerow(line)
    filename = 'attachment; filename=Starterlizenz-{0}-{1}-{2}-{3}.csv'.format(pk,
                                                                               today.year,
                                                                               today.month,
                                                                               today.day)
    response['Content-Disposition'] = filename
    response['Content-Length'] = len(response.content)
    submission.update(mail_merge=True)
    return response


def export_csv_new(request):
    '''
    Exports all submissions that have not been exported for mailmerge
    '''
    if not request.user.has_perm('submission.change_submissionstarter'):
        return HttpResponseForbidden()

    response = HttpResponse(mimetype='text/csv')
    writer = csv.writer(response, delimiter='\t')
    today = datetime.date.today()

    submissions = SubmissionStarter.objects.filter(mail_merge=False) \
        .filter(submission_status=SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT) \
        .select_related()

    # Write the CSV file
    writer.writerow(MAILMERGE_HEADER)
    for line in export_submission_mailmerge(submissions):
        writer.writerow(line)
    filename = 'attachment; filename=Starterlizenzen-{0}-{1}-{2}.csv'.format(today.year,
                                                                             today.month,
                                                                             today.day)
    response['Content-Disposition'] = filename
    response['Content-Length'] = len(response.content)
    submissions.update(mail_merge=True)
    return response
