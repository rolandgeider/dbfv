# -*- coding: utf-8 *-*

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import csv
import datetime

from django.core.management.base import BaseCommand, CommandError

from submission.models import Gym


class Command(BaseCommand):
    '''
    Export all submissions for the current year
    '''

    def export_submission_mailmerge(self, gym_list):
        '''
        Generates a list with starter submission fields to be used in mail merge

        :param submission_list: A list of Submissions
        '''
        result = []
        for gym in gym_list:
            result.append([unicode(s).encode("utf-8") for s in [gym.name, gym.email, gym.state.name, gym.owner, gym.zip_code, gym.city, gym.street, gym.is_active]])
        return result

    def handle(self, *args, **options):
        '''
        Process the options
        '''
        #gym_list = Gym.objects.filter(state_id=1, is_active=True)
        gym_list = Gym.objects.filter(is_active=False)

        with open('gym.csv', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter='\t',quoting=csv.QUOTE_ALL)

            # Write the CSV file
            writer.writerow(['Name', 'E-Mail', 'Bundesland', 'Inhaber', 'PLZ', 'Stadt', 'Adresse', 'Aktiv'])
            for line in self.export_submission_mailmerge(gym_list):
                writer.writerow(line)
