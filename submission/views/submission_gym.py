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

from submission.forms import SubmissionGymForm, SubmissionGymFormBV
from submission.models import SubmissionGym
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


class SubmissionCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new submissions
    '''

    model = SubmissionGym
    form_class = SubmissionGymForm
    permission_required = 'submission.add_submissiongym'
    template_name = 'submission/gym/create.html'
    page_title = 'Antrag auf Erwerb einer Studiolizenz'

    def form_valid(self, form):
        '''
        Manually set the user when saving the form
        '''

        form.instance.user = self.request.user
        self.form_instance = form.instance
        return super(SubmissionCreateView, self).form_valid(form)

    def get_success_url(self):
        self.form_instance.send_emails()

        self.request.session['bank-account'] = self.form_instance.get_bank_account()
        self.request.session['submission-fee'] = SubmissionGym.FEE
        self.request.session['designated-use'] = u'Studiolizenz {0}<br>\n{1}'.format(self.object.pk,
                                                                                     self.object.get_name)
        return reverse_lazy('bank-account-view')

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all states
        '''
        context = super(SubmissionCreateView, self).get_context_data(**kwargs)
        context['states_list'] = State.objects.all()
        return context


class SubmissionDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a submission
    '''

    model = SubmissionGym
    success_url = reverse_lazy('submission-studio-list')
    permission_required = 'submission.delete_submissiongym'
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

    model = SubmissionGym
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submissiongym'


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = SubmissionGym
    form_class = SubmissionGymFormBV
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submissiongym'
