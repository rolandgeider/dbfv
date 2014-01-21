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

from submission.models import BankAccount

from submission.views.generic_views import DbfvViewMixin
from submission.views.generic_views import DbfvFormMixin


class BankAccountListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all bank accounts
    '''

    context_object_name = "account_list"
    model = BankAccount
    template_name = 'bank_account/list.html'
    permission_required = 'submission.change_bankaccount'


class BankAccountDetailView(DbfvViewMixin, generic.DetailView):
    '''
    Detail view of a bank account
    '''

    model = BankAccount
    template_name = 'bank_account/view.html'
    login_required = True

    def get_object(self):
        '''
        Load the account by the ID in the session
        '''
        return BankAccount.objects.get(pk=self.request.session['bank-account'])


class BankAccountCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new bank account
    '''

    model = BankAccount
    success_url = reverse_lazy('bank-account-list')
    permission_required = 'submission.add_bankaccount'


class BankAccountUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Edits a bank account
    '''

    model = BankAccount
    success_url = reverse_lazy('bank-account-list')
    permission_required = 'submission.change_bankaccount'
