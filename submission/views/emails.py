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
from django.urls import reverse_lazy
from django.views import generic

from submission.models import ManagerEmail

from submission.views.generic_views import DbfvViewMixin
from submission.views.generic_views import DbfvFormMixin


class EmailListView(DbfvViewMixin, generic.ListView):
    """
    Shows a list with all manager emails
    """

    model = ManagerEmail
    context_object_name = "email_list"
    template_name = 'email/list.html'
    permission_required = 'submission.add_manageremail'
    login_required = True


class EmailCreateView(DbfvFormMixin, generic.CreateView):
    """
    Creates a new federal state
    """

    model = ManagerEmail
    success_url = reverse_lazy('email-list')
    permission_required = 'submission.add_manageremail'


class EmailUpdateView(DbfvFormMixin, generic.UpdateView):
    """
    Updates a federal state
    """

    model = ManagerEmail
    success_url = reverse_lazy('email-list')
    permission_required = 'submission.change_manageremail'


class EmailDeleteView(DbfvFormMixin, generic.DeleteView):
    """
    Deletes a state
    """

    model = ManagerEmail
    success_url = reverse_lazy('email-list')
    permission_required = 'submission.delete_manageremail'
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        """
        Pass the title to the context
        """
        context = super(EmailDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Email {0} löschen?'.format(self.object.email)
        return context
