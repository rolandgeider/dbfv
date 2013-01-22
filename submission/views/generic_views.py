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

from django.views.generic.base import TemplateResponseMixin
from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden


class DbfvViewMixin(TemplateResponseMixin):
    permission_required = ''
    login_required = False

    def dispatch(self, request, *args, **kwargs):

        # Check for necessary permissions
        if self.login_required or self.permission_required:
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('index')+'?next=%s' % request.path)

            if self.permission_required and \
                not request.user.has_perm(self.permission_required):
                return HttpResponseForbidden()

        return super(DbfvViewMixin, self).dispatch(request, *args, **kwargs)


class DbfvFormMixin(DbfvViewMixin):

    template_name = 'form.html'

    def get_context_data(self, **kwargs):
        '''
        Set the context data
        '''

        context = super(DbfvFormMixin, self).get_context_data(**kwargs)
        context['form_action'] = self.get_form_action()
        context['title'] = self.page_title

        return context
