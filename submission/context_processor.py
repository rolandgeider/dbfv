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

# dbfv
from submission.models import (
    USER_TYPE_BUNDESVERBAND,
    USER_TYPE_USER,
    SubmissionStarter,
    user_type,
)


def processor(request):
    return {
        # User type
        'user_type': user_type(request.user),

        # User types
        'USER_TYPE_BUNDESVERBAND': USER_TYPE_BUNDESVERBAND,
        'USER_TYPE_USER': USER_TYPE_USER,

        # Submission stati
        'SUBMISSION_STATUS_EINGEGANGEN': SubmissionStarter.SUBMISSION_STATUS_EINGEGANGEN,
        'SUBMISSION_STATUS_BEWILLIGT': SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT,
        'SUBMISSION_STATUS_ABGELEHNT': SubmissionStarter.SUBMISSION_STATUS_ABGELEHNT,
    }
