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
from django.http import HttpResponseForbidden

from django.views import generic
from django.core.urlresolvers import reverse_lazy

from submission.forms import SubmissionGymForm, SubmissionGymFormBV
from submission.models import SubmissionGym, Gym
from submission.models import State
from submission.models import user_type
from submission.models import USER_TYPE_BUNDESVERBAND
from submission.models import USER_TYPE_USER
from submission.views.generic_views import DbfvViewMixin
from submission.views.generic_views import BaseSubmissionCreateView
from submission.views.generic_views import BaseSubmissionDeleteView
from submission.views.generic_views import BaseSubmissionUpdateView
from submission.views.generic_views import DbfvFormMixin


class SubmissionListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all submissions
    '''

    model = SubmissionGym
    context_object_name = "submission_list"
    template_name = 'submission/gym/list.html'
    login_required = True

    def get_queryset(self):
        '''
        Change the queryset depending on the user's rights. The rules are the
        follwing:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        '''

        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return SubmissionGym.objects.all()
        elif user_type(self.request.user) == USER_TYPE_USER:
            return SubmissionGym.objects.filter(user=self.request.user)


class SubmissionListYearView(SubmissionListView, generic.dates.YearMixin):
    def get_queryset(self):
        '''
        Change the queryset depending on the user's rights. The rules are the
        follwing:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        '''

        # Get queryset from parent class
        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return SubmissionGym.objects.filter(creation_date__year=self.get_year())
        elif user_type(self.request.user) == USER_TYPE_USER:
            return SubmissionGym.objects.filter(user=self.request.user,
                                                creation_date__year=self.get_year())


class SubmissionDetailView(DbfvViewMixin, generic.detail.DetailView):
    login_required = True
    model = SubmissionGym
    template_name = 'submission/gym/view.html'

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for necessary permissions
        '''
        submission = self.get_object()
        if not request.user.has_perm('submission.delete_submissiongym') \
           and submission.user != request.user:
            return HttpResponseForbidden()

        # Save submission data to the session
        self.request.session['bank-account'] = submission.get_bank_account()
        self.request.session['submission-fee'] = submission.FEE
        self.request.session['designated-use'] = submission.get_bank_designated_use()
        return super(SubmissionDetailView, self).dispatch(request, *args, **kwargs)


class SubmissionCreateView(BaseSubmissionCreateView):
    '''
    Creates a new submissions
    '''

    model = SubmissionGym
    form_class = SubmissionGymForm
    permission_required = 'submission.add_submissiongym'
    template_name = 'submission/gym/create.html'
    page_title = 'Antrag auf Erwerb einer Studiolizenz'

    def get_success_url(self):
        '''
        If the form is valid, create a new gym with the form data.

        Performing the logic here because we need access to the submission PK
        '''

        gym = Gym()
        gym.name = self.object.name
        gym.email = self.object.email
        gym.state = self.object.state
        gym.owner = ''
        gym.zip_code = self.object.zip_code
        gym.city = self.object.city
        gym.street = self.object.street
        gym.is_active = False
        gym.submission = self.object
        gym.save()

        self.object.gym = gym
        self.object.save()

        return super(SubmissionCreateView, self).get_success_url()


class SubmissionDeleteView(BaseSubmissionDeleteView):
    '''
    Deletes a submission
    '''
    model = SubmissionGym
    success_url = reverse_lazy('submission-studio-list')


class SubmissionUpdateView(BaseSubmissionUpdateView):
    '''
    Updates an existing submission
    '''
    model = SubmissionGym
    form_class = SubmissionGymForm


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = SubmissionGym
    form_class = SubmissionGymFormBV
    success_url = reverse_lazy('submission-studio-list')
    permission_required = 'submission.change_submissiongym'

    def form_valid(self, form):
        '''
        If the submission is accepted, activate the gym
        '''

        if form.cleaned_data['submission_status'] == SubmissionGym.SUBMISSION_STATUS_BEWILLIGT:
            gym = form.instance.gym
            gym.is_active = True
            gym.save()

        return super(SubmissionUpdateStatusView, self).form_valid(form)