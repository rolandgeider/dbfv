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
from submission.models import user_type
from submission.models import user_lv
from submission.models import USER_TYPE_LANDESVERBAND
from submission.models import USER_TYPE_BUNDESVERBAND
from submission.models import USER_TYPE_USER
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

    def get_queryset(self):
        '''
        Change the queryset depending on the user's rights. The rules are the
        follwing:
            * A BC user sees all submissions
            * A LV user sees the submissions for all gyms in his state
            * A regular user sees it's own submissions
        '''

        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return Submission.objects.all()
        elif user_type(self.request.user) == USER_TYPE_LANDESVERBAND:
            return Submission.objects.filter(gym__state=user_lv(self.request.user))
        elif user_type(self.request.user) == USER_TYPE_USER:
            return Submission.objects.filter(user=self.request.user)
        #else:
        #    pass


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
    #template_name = 'submission/form.html'

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


class SubmissionFormLV(ModelForm):
    class Meta:
        model = Submission
        exclude = ('user',
                   'gym',
                   'anhang',
                   'submission_status_bv',
                   'submission_type')


class SubmissionFormBV(ModelForm):
    class Meta:
        model = Submission
        exclude = ('user',
                   'gym',
                   'anhang',
                   'submission_status_lv',
                   'submission_type')


class SubmissionUpdateStatusView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submissions
    '''

    model = Submission
    success_url = reverse_lazy('submission-list')
    permission_required = 'submission.change_submission'

    def get_form_class(self):
        '''
        Return the Form class, depending on the user type (LV or BV)
        '''

        if user_type(self.request.user) == USER_TYPE_BUNDESVERBAND:
            return SubmissionFormBV
        elif user_type(self.request.user) == USER_TYPE_LANDESVERBAND:
            return SubmissionFormLV
