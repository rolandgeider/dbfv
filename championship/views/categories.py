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

from championship.models import Category, category_fields
from submission.views.generic_views import DbfvViewMixin, DbfvFormMixin


class CategoriesListView(DbfvViewMixin, generic.ListView):
    '''
    Shows a list with all championship categories
    '''

    model = Category
    context_object_name = "categories_list"
    template_name = 'categories/list.html'
    permission_required = 'championship.add_category'
    login_required = True


class CategoryCreateView(DbfvFormMixin, generic.CreateView):
    '''
    Creates a new federal state
    '''

    model = Category
    fields = category_fields
    success_url = reverse_lazy('championship:category:list')
    permission_required = 'championship.add_category'


class CategoryUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates a federal state
    '''

    model = Category
    fields = category_fields
    success_url = reverse_lazy('championship:category:list')
    permission_required = 'championship.change_category'


class CategoryDeleteView(DbfvFormMixin, generic.DeleteView):
    '''
    Deletes a state
    '''

    model = Category
    success_url = reverse_lazy('championship:category:list')
    permission_required = 'championship.delete_category'
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        '''
        Pass the title to the context
        '''
        context = super(CategoryDeleteView, self).get_context_data(**kwargs)
        context['title'] = u'Kategorie {0} löschen?'.format(self.object.name)
        return context
