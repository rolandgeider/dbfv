# -*- coding: utf-8 *-*

# This file is part of the DBFV submission site
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import csv
import datetime

# Django
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

# dbfv
from submission.models import SubmissionStarter


class Command(BaseCommand):
    """
    Export all submissions for the current year
    """

    def export_submission_mailmerge(self, submission_list):
        """
        Generates a list with starter submission fields to be used in mail merge

        :param submission_list: A list of Submissions
        """
        result = []
        for submission in submission_list:
            result.append([unicode(s).encode("utf-8") for s in submission.get_mailmerge_row()])
        return result

    def handle(self, *args, **options):
        """
        Process the options
        """
        list = SubmissionStarter.objects.filter(
            creation_date__year=2014,
            submission_status=SubmissionStarter.SUBMISSION_STATUS_BEWILLIGT
        ).order_by('id')

        with open('starter.csv', 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
            today = datetime.date.today()
            submissions = list

            # Write the CSV file
            writer.writerow(SubmissionStarter.MAILMERGE_HEADER)
            for line in self.export_submission_mailmerge(submissions):
                writer.writerow(line)
