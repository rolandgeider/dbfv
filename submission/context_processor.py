# -*- coding: utf-8 -*-

# This file is part of Kumasta.
#
# Kumasta is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Kumasta is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Kumasta.  If not, see <http://www.gnu.org/licenses/>.


from submission.models import user_type

from submission.models import USER_TYPE_BUNDESVERBAND
from submission.models import USER_TYPE_USER

from submission.models import SUBMISSION_STATUS_EINGEGANGEN
from submission.models import SUBMISSION_STATUS_BEWILLIGT
from submission.models import SUBMISSION_STATUS_ABGELEHNT


def processor(request):
    return {
        # User type
        'user_type': user_type(request.user),

        # User types
        'USER_TYPE_BUNDESVERBAND': USER_TYPE_BUNDESVERBAND,
        'USER_TYPE_USER': USER_TYPE_USER,

        # Submission stati
        'SUBMISSION_STATUS_EINGEGANGEN': SUBMISSION_STATUS_EINGEGANGEN,
        'SUBMISSION_STATUS_BEWILLIGT': SUBMISSION_STATUS_BEWILLIGT,
        'SUBMISSION_STATUS_ABGELEHNT': SUBMISSION_STATUS_ABGELEHNT,

    }
