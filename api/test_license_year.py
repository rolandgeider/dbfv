"""The license calendar follows the application's Berlin timezone."""

from datetime import datetime, timezone as dt_timezone
from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from api.tests import _federal_key, _make_starter
from submission.models import SubmissionStarter


@override_settings(TIME_ZONE='Europe/Berlin')
class LicenseCalendarTest(APITestCase):
    def setUp(self):
        self.submission = _make_starter()
        SubmissionStarter.objects.filter(pk=self.submission.pk).update(creation_date='2027-01-01')
        _, key = _federal_key(
            name='calendar', sensitive_access=True,
            allow_export_licenses=True, allow_lookup_licenses=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')

    @patch('django.utils.timezone.now', return_value=datetime(2026, 12, 31, 23, 30, tzinfo=dt_timezone.utc))
    def test_new_year_defaults_and_validation_follow_local_calendar(self, _now):
        export = self.client.get('/api/v1/licenses/valid/')
        self.assertEqual(export.status_code, 200)
        self.assertEqual(export.data['count'], 1)
        self.assertEqual(export.data['results'][0]['year'], 2027)
        lookup_data = {'last_name': self.submission.last_name, 'email': self.submission.email}
        lookup = self.client.post('/api/v1/licenses/lookup/', lookup_data, format='json')
        self.assertEqual(lookup.status_code, 200)
        self.assertEqual(lookup.data['year'], 2027)
        self.assertTrue(lookup.data['valid'])
        for year, expected in ((2028, 200), (2029, 400)):
            self.assertEqual(self.client.get('/api/v1/licenses/valid/', {'year': year}).status_code, expected)
            self.assertEqual(self.client.post(
                '/api/v1/licenses/lookup/', dict(lookup_data, year=year), format='json'
            ).status_code, expected)
