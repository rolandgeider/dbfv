# -*- coding: utf-8 -*-

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
"""
Simple script that filters the output of django's dumpdata command into more
manageable chunks.

Create the data.json e.g. with:
    python ../../manage.py dumpdata --indent=4 > data.json
"""

import json


def filter_dump(data, model_list, filename):
    """
    Helper function
    """
    filter_data = [i for i in data if i['model'] in model_list]
    with open(filename, 'w') as outfile:
        json.dump(filter_data, outfile, indent=4)


# This is a full dump of the DB
fixture = open('data.json')
data = json.load(fixture)
fixture.close()

#
# Submission
#
filter_dump(data, ('submission.manageremail', ), 'manageremail.json')
filter_dump(data, ('submission.bankaccount', ), 'bank_account.json')
filter_dump(data, ('submission.state', ), 'federal_states.json')
filter_dump(data, ('submission.gym', ), 'gyms.json')
filter_dump(data, ('submission.submissiongym', ), 'submission_gym.json')
filter_dump(data, ('submission.submissionstarter', ), 'submission_starter.json')

#
# Auth
#
filter_dump(data, ('auth.group', ), 'groups.json')
