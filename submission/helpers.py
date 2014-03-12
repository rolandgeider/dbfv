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

MAILMERGE_HEADER = ['ID',
                    'Vorname',
                    'Nachname',
                    'Geburtsdatum',
                    'Aktiv Seit',
                    'Straße',
                    'PLZ',
                    'Stadt',
                    'Telefon',
                    'Email',
                    'Nationalität',
                    'Größe',
                    'Gewicht',
                    'Kategorie',
                    'Studio',
                    'Bundesverband',
                    'Datum',
                    'Jahr',]


def export_submission_mailmerge(submission_list):
    '''
    Generates a list with starter submission fields to be used in mail merge

    :param submission_list: A list of Submissions
    '''
    result = []
    for submission in submission_list:
        tmp = [submission.pk,
               submission.first_name,
               submission.last_name,
               submission.date_of_birth,
               submission.active_since,
               submission.street,
               submission.zip_code,
               submission.city,
               submission.tel_number,
               submission.email,
               submission.nationality.name,
               submission.height,
               submission.weight,
               submission.get_category_display(),
               submission.gym.name,
               submission.gym.state,
               submission.creation_date,
               submission.creation_date.year,]
        result.append([unicode(s).encode("utf-8") for s in tmp])
    return result
