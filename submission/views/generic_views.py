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
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin
from django.core.urlresolvers import reverse, reverse_lazy

from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden


class DbfvViewMixin(TemplateResponseMixin):
    permission_required = ''
    login_required = False

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for necessary permissions
        '''
        if self.login_required or self.permission_required:
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('login') + '?next=%s' % request.path)

            if self.permission_required and \
                    not request.user.has_perm(self.permission_required):
                return HttpResponseForbidden()

        return super(DbfvViewMixin, self).dispatch(request, *args, **kwargs)


class DbfvFormMixin(DbfvViewMixin, ModelFormMixin):

    page_title = ''
    template_name = 'form.html'

    def get_context_data(self, **kwargs):
        '''
        Set the context data
        '''

        context = super(DbfvFormMixin, self).get_context_data(**kwargs)
        context['form_action'] = self.request.get_full_path()
        context['title'] = self.page_title

        return context


#
# Submissions
#

class BaseSubmissionCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new submissions
    '''

    def form_valid(self, form):
        '''
        Manually set the user when saving the form
        '''

        form.instance.user = self.request.user
        return super(BaseSubmissionCreateView, self).form_valid(form)

    def get_success_url(self):
        '''
        Redirect to bank account page and send appropriate emails
        '''
        self.object.send_emails()
        self.request.session['bank-account'] = self.object.get_bank_account()
        self.request.session['submission-fee'] = self.model.FEE
        self.request.session['designated-use'] = self.object.get_bank_designated_use()

        return reverse_lazy('bank-account-view')

    def get_context_data(self, **kwargs):
        '''
        Pass a list of all states
        '''
        context = super(BaseSubmissionCreateView, self).get_context_data(**kwargs)
        context['fee'] = self.model.FEE
        return context

    def get_initial(self):
        '''
        Fill in some data
        '''
        return {'email': self.request.user.email}


class BaseSubmissionDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a submission
    '''

    permission_required = 'submission.delete_submissiongym'
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        '''
        Pass the title to the context
        '''
        context = super(BaseSubmissionDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Antrag {0} löschen?'.format(self.object.id)
        return context


class BaseSubmissionUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates an existing submission

    The owner user can update his own submission while it is still in the
    pending state. Once it has been accepted, only the BV can edit it.
    '''

    login_required = True
    page_title = 'Antrag bearbeiten'

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for necessary permissions
        '''
        submission = self.get_object()
        if not request.user.has_perm('submission.delete_submissionstarter') \
            and (submission.submission_status != submission.SUBMISSION_STATUS_EINGEGANGEN
                 or submission.user != request.user):
            return HttpResponseForbidden(u'Sie dürfen dieses Objekt nicht editieren!')

        return super(BaseSubmissionUpdateView, self).dispatch(request, *args, **kwargs)
