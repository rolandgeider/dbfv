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
import datetime

# Django
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.utils import timezone

# dbfv
from submission.models import (
    SubmissionStarter,
    SubmissionInternational,
    SubmissionJudge,
)


class Command(BaseCommand):
    """
    Closes all open submissions that are older than a number of months (default 4)
    """

    def add_arguments(self, parser):
        """Add command line arguments.

        --model: Which submission model to operate on; required. Allowed values: starter, international, judge
        --months: Number of months to use as cutoff (positive integer). Default is 4.
        --dry-run: If set, don't actually save changes; just report what would be closed.
        """
        parser.add_argument(
            '--model',
            required=True,
            choices=['starter', 'international', 'judge'],
            help='Submission model to operate on: starter, international or judge (required)'
        )
        parser.add_argument(
            '--months',
            type=int,
            default=4,
            help='Number of months; submissions older than this will be closed (default: 4)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Don't persist changes; only report how many submissions would be closed."
        )

    def handle(self, *args, **options):
        """
        Process the options
        """
        model_choice = options.get('model')
        months = options.get('months', 4)
        dry_run = options.get('dry_run', False)

        # validate months
        try:
            months = int(months)
        except (TypeError, ValueError):
            raise CommandError('The --months value must be an integer.')
        if months <= 0:
            raise CommandError('The --months value must be a positive integer.')

        # map the choice to the actual model class
        models_map = {
            'starter': SubmissionStarter,
            'international': SubmissionInternational,
            'judge': SubmissionJudge,
        }
        try:
            model_cls = models_map[model_choice]
        except KeyError:
            raise CommandError('Unknown model: {0}'.format(model_choice))

        # All submission models share the same status constants and field names via AbstractSubmission
        open_status = getattr(model_cls, 'SUBMISSION_STATUS_EINGEGANGEN')
        closed_status = getattr(model_cls, 'SUBMISSION_STATUS_ABGELEHNT')
        status_field = 'submission_status'
        cutoff_date = timezone.now() - datetime.timedelta(days=months * 30)

        # build filter kwargs dynamically
        filter_kwargs = {
            status_field: open_status,
            'creation_date__lt': cutoff_date,
        }
        open_submissions = model_cls.objects.filter(**filter_kwargs)
        count = open_submissions.count()

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN: Would close {count} {model_choice} submissions older than {months} months.'
                )
            )
            return

        for submission in open_submissions:
            setattr(submission, status_field, closed_status)
            submission.save()
        self.stdout.write(
            self.style.SUCCESS(
                f'Closed {count} {model_choice} submissions older than {months} months.'
            )
        )
