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

from django.core.urlresolvers import reverse_lazy, reverse
from django.views import generic

from championship.models import Assessment, assessment_fields
from submission.views.generic_views import DbfvFormMixin


class CategoryUpdateView(DbfvFormMixin, generic.UpdateView):
    '''
    Updates a federal state
    '''

    model = Assessment
    fields = assessment_fields
    success_url = reverse_lazy('championship:category:list')
    permission_required = 'championship.change_assessment'

    def get_success_url(self):
        return reverse('championship:championship:category-detail',
                       kwargs={'pk': self.object.collection.championship.pk,
                               'category_pk': self.object.collection.category.pk})