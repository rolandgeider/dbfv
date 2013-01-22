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

from submission.models import Gym
from submission.views.generic_views import DbfvViewMixin
from submission.views.generic_views import DbfvFormMixin


class GymListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all konzepts
    '''

    context_object_name = "gym_list"
    model = Gym
    template_name = 'gym/list.html'
    login_required = True


class GymDetailView(DbfvViewMixin, generic.DetailView):
    '''
    Detail view of a gym
    '''

    model = Gym
    template_name = 'gym/view.html'
    login_required = True


class GymCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Shows a list with all konzepts
    '''

    model = Gym
    permission_required = 'submission.add_gym'


class GymUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Edits an existing Gym
    '''

    model = Gym
    permission_required = 'submission.change_gym'
