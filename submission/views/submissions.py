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
        follwing:
            * A BV user sees all submissions
            * A regular user sees it's own submissions
        '''

        print user_type(self.request.user)
        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return SubmissionStarter.objects.all()
        elif user_type(self.request.user) == USER_TYPE_USER:
            return SubmissionStarter.objects.filter(user=self.request.user)


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
            return SubmissionStarter.objects.filter(creation_date__year=self.get_year())
        elif user_type(self.request.user) == USER_TYPE_USER:
            return SubmissionStarter.objects.filter(user=self.request.user,
                                            creation_date__year=self.get_year())


class SubmissionForm(ModelForm):
    class Meta:
        model = SubmissionStarter
        exclude = ('submission_status',)


class SubmissionNoFileForm(ModelForm):
    class Meta:
        model = SubmissionStarter
        exclude = ('submission_status', 'anhang')


class SubmissionCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new submissions
    '''

    model = SubmissionStarter
    form_class = SubmissionForm
    success_url = reverse_lazy('index')
    permission_required = 'submission.add_submissionstarter'
    template_name = 'submission/create.html'

    def form_valid(self, form):
        '''
        Manually set some values when saving the form
        '''

        # Set the user
        form.instance.user = self.request.user

        self.form_instance = form.instance
        return super(SubmissionCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('bank-account-view',
                            kwargs={'pk': self.form_instance.gym.state.bank_account_id})

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

    model = SubmissionStarter
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.delete_submission'
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

    model = SubmissionStarter
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submission'


class SubmissionFormBV(ModelForm):
    class Meta:
        model = SubmissionStarter
        fields = ('submission_status', )


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = SubmissionStarter
    form_class = SubmissionFormBV
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submission'
