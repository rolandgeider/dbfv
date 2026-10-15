# Third Party
from rest_framework import status
from rest_framework.test import APITestCase

# Django
from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import RequestFactory, override_settings

# dbfv
from api.models import APIAccessLog, ScopedAPIKey
from core.models import EmailCron
from submission.models import (
    BankAccount,
    Country,
    Gym,
    ManagerEmail,
    State,
    SubmissionStarter,
    UserProfile,
)


class ScopedAPIKeyPermissionTest(APITestCase):
    """Read for any valid key; write only with write_allowed."""

    @classmethod
    def setUpTestData(cls):
        _, cls.rw = ScopedAPIKey.objects.create_key(
            name='rw', write_allowed=True, federal_access=True
        )
        _, cls.ro = ScopedAPIKey.objects.create_key(name='ro', write_allowed=False)
        Country.objects.create(name='Germany')

    def _auth(self, key):
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')

    def test_no_key_denied(self):
        self.assertEqual(self.client.get('/api/v1/country/').status_code, status.HTTP_403_FORBIDDEN)

    def test_read_only_key_can_read(self):
        self._auth(self.ro)
        self.assertEqual(self.client.get('/api/v1/country/').status_code, status.HTTP_200_OK)

    def test_read_only_key_cannot_write(self):
        self._auth(self.ro)
        res = self.client.post('/api/v1/country/', {'name': 'France'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_write_key_can_write(self):
        self._auth(self.rw)
        res = self.client.post('/api/v1/country/', {'name': 'France'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Country.objects.filter(name='France').exists())

    def test_submission_endpoint_is_read_only(self):
        # Submissions expose no write actions (user field editable=False,
        # status changes must run through the domain workflow).
        _, key = ScopedAPIKey.objects.create_key(
            name='sw',
            write_allowed=True,
            sensitive_access=True,
            federal_access=True,
            allow_read_submissions=True,
        )
        self._auth(key)
        res = self.client.post('/api/v1/submissionstarter/', {}, format='json')
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_requires_sensitive_access(self):
        # DELETE on open Stammdaten cascades into sensitive submissions.
        self._auth(self.rw)
        country = Country.objects.create(name='Italy')
        res = self.client.delete(f'/api/v1/country/{country.pk}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_ip_allowlist_blocks_foreign_ip(self):
        _, key = ScopedAPIKey.objects.create_key(name='ip', allowed_ips='10.0.0.1')
        self._auth(key)
        res = self.client.get('/api/v1/country/', REMOTE_ADDR='203.0.113.9')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_ip_allowlist_permits_listed_cidr(self):
        _, key = ScopedAPIKey.objects.create_key(name='ip2', allowed_ips='203.0.113.0/24')
        self._auth(key)
        res = self.client.get('/api/v1/country/', REMOTE_ADDR='203.0.113.9')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_forged_forwarded_for_is_ignored_by_default(self):
        # No trusted proxy configured -> X-Forwarded-For must not grant access.
        _, key = ScopedAPIKey.objects.create_key(name='ip3', allowed_ips='10.0.0.1')
        self._auth(key)
        res = self.client.get(
            '/api/v1/country/',
            REMOTE_ADDR='203.0.113.9',
            HTTP_X_FORWARDED_FOR='10.0.0.1',
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_exact_filter(self):
        Country.objects.create(name='Spain')
        self._auth(self.ro)
        res = self.client.get('/api/v1/country/', {'name': 'Spain'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_search(self):
        Country.objects.create(name='Spain')
        self._auth(self.ro)
        res = self.client.get('/api/v1/country/', {'search': 'pai'})
        self.assertEqual([c['name'] for c in res.data['results']], ['Spain'])

    def test_ordering(self):
        Country.objects.create(name='Austria')
        self._auth(self.ro)
        res = self.client.get('/api/v1/country/', {'ordering': 'name'})
        names = [c['name'] for c in res.data['results']]
        self.assertEqual(names, sorted(names))

    @override_settings(API_PREAUTH_RATE_LIMIT='2/minute')
    def test_invalid_keys_are_rate_limited_before_permissions(self):
        cache.clear()
        for prefix in ('AAAA0001', 'BBBB0002'):
            res = self.client.get(
                '/api/v1/country/',
                HTTP_AUTHORIZATION=f'Api-Key {prefix}.invalid',
                REMOTE_ADDR='203.0.113.50',
            )
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(
            '/api/v1/country/',
            HTTP_AUTHORIZATION='Api-Key CCCC0003.invalid',
            REMOTE_ADDR='203.0.113.50',
        )
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', res)


class SensitiveScopeTest(APITestCase):
    def test_sensitive_model_needs_scope(self):
        _, plain = ScopedAPIKey.objects.create_key(name='plain')
        _, priv = ScopedAPIKey.objects.create_key(
            name='priv',
            sensitive_access=True,
            federal_access=True,
            allow_read_submissions=True,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {plain}')
        self.assertEqual(
            self.client.get('/api/v1/bankaccount/').status_code, status.HTTP_403_FORBIDDEN
        )
        # non-sensitive Stammdaten stay open
        self.assertEqual(self.client.get('/api/v1/country/').status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {priv}')
        self.assertEqual(
            self.client.get('/api/v1/bankaccount/').status_code, status.HTTP_200_OK
        )


class ThrottleKeyTest(APITestCase):
    def test_cache_key_uses_key_prefix_not_secret(self):
        # dbfv
        from api.throttling import APIKeyRateThrottle

        throttle = APIKeyRateThrottle()

        class _Req:
            META = {'HTTP_AUTHORIZATION': 'Api-Key ABCD1234.longsecretvalue'}

        cache_key = throttle.get_cache_key(_Req(), None)
        self.assertIn('ABCD1234', cache_key)
        self.assertNotIn('longsecretvalue', cache_key)


class ApiKeyRequestFormTest(APITestCase):
    # Note: the view is exercised live; a Client-based render test hits a
    # Python 3.14 x Django 5.1 bug in the test client's template
    # instrumentation (Context.__copy__), unrelated to this code. We test the
    # only non-trivial logic — the honeypot — directly on the form.
    def _data(self, **over):
        data = {
            'name': 'Max', 'organization': 'DBFV NRW', 'email': 'max@nrw.de',
            'intended_use': 'Lizenzabgleich', 'website': '',
        }
        data.update(over)
        return data

    def setUp(self):
        cache.clear()

    def test_valid_without_honeypot(self):
        # dbfv
        from api.contact import ApiKeyRequestForm

        self.assertTrue(ApiKeyRequestForm(data=self._data()).is_valid())

    def test_honeypot_blocks_spam(self):
        # dbfv
        from api.contact import ApiKeyRequestForm

        self.assertFalse(ApiKeyRequestForm(data=self._data(website='http://spam')).is_valid())

    @override_settings(API_KEY_REQUEST_RATE_LIMIT='2/hour')
    def test_post_is_rate_limited_by_ip(self):
        # RequestFactory avoids the Python 3.14/Django 5.1 test-client
        # template instrumentation bug documented above.
        from django.contrib.auth.models import AnonymousUser

        from api.contact import api_key_request

        payload = self._data(website='http://spam')
        factory = RequestFactory()
        responses = []
        for _ in range(3):
            request = factory.post(
                '/api-key/anfrage', payload, REMOTE_ADDR='203.0.113.8'
            )
            request.user = AnonymousUser()
            responses.append(api_key_request(request))
        self.assertEqual(responses[0].status_code, 200)
        self.assertEqual(responses[1].status_code, 200)
        response = responses[2]
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Retry-After', response)


class SchemaTest(APITestCase):
    def test_schema_public(self):
        # Schema/docs are served without an API key.
        res = self.client.get('/api/v1/schema/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


def _make_starter(
    dob='1990-05-01',
    submission_status='2',
    state_name='NRW',
    state_short='NRW',
    last_name='Mustermann',
    first_name='Max',
    email='m@x.de',
):
    """Create a SubmissionStarter with all required relations."""
    bank = BankAccount.objects.create(
        owner_name=f'DBFV {state_short}', iban=f'DE00{state_short}', bic='X',
        bank_name='Bank',
    )
    state = State.objects.create(name=state_name, short_name=state_short, bank_account=bank)
    gym = Gym.objects.create(name=f'Muscle Gym {state_short}', state=state)
    country = Country.objects.create(name='Germany')
    user = User.objects.create(username=f'u{dob}{submission_status}{state_short}')
    return SubmissionStarter.objects.create(
        user=user, date_of_birth=dob, active_since='2010', last_name=last_name,
        first_name=first_name, street='Weg', house_nr='1', zip_code=12345, city='Köln',
        tel_number='0', email=email, nationality=country, height=180, weight=80,
        category='1', terms_and_conditions=True, gym=gym,
        submission_status=submission_status,
    )


def _scoped_key_for(*states, sensitive_access=True, write_allowed=False, **kwargs):
    api_key, key = ScopedAPIKey.objects.create_key(
        name='scoped',
        sensitive_access=sensitive_access,
        write_allowed=write_allowed,
        **kwargs,
    )
    api_key.allowed_states.add(*states)
    return api_key, key


def _federal_key(**kwargs):
    return ScopedAPIKey.objects.create_key(federal_access=True, **kwargs)


class LicenseEndpointTest(APITestCase):
    def setUp(self):
        _, self.plain = _federal_key(name='lic', allow_lookup_licenses=True)
        _, self.priv = _federal_key(
            name='lic-priv',
            sensitive_access=True,
            allow_lookup_licenses=True,
            allow_export_licenses=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.plain}')

    def test_bulk_needs_sensitive_scope(self):
        # plain key: bulk export forbidden
        self.assertEqual(
            self.client.get('/api/v1/licenses/valid/').status_code, status.HTTP_403_FORBIDDEN
        )

    def test_bulk_needs_export_scope(self):
        _, key = _federal_key(name='no-export', sensitive_access=True)
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')
        self.assertEqual(
            self.client.get('/api/v1/licenses/valid/').status_code, status.HTTP_403_FORBIDDEN
        )

    def test_valid_lists_approved_with_sensitive_key(self):
        _make_starter(submission_status='2')
        _make_starter(dob='1985-01-01', submission_status='1')  # Eingegangen -> not valid
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.priv}')
        res = self.client.get('/api/v1/licenses/valid/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # paginated response
        self.assertEqual(res.data['count'], 1)
        result = res.data['results'][0]
        self.assertEqual(result['license_type'], 'starter')
        # minimal by default: no date_of_birth unless requested
        self.assertNotIn('date_of_birth', result)

    def test_valid_includes_dob_only_on_request(self):
        _make_starter(dob='1990-05-01', submission_status='2')
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.priv}')
        res = self.client.get('/api/v1/licenses/valid/', {'include': 'date_of_birth'})
        self.assertEqual(res.data['results'][0]['date_of_birth'], '1990-05-01')

    def test_lookup_match_minimal_output(self):
        _make_starter(dob='1990-05-01', submission_status='2')
        res = self.client.post(
            '/api/v1/licenses/lookup/',
            {'last_name': 'Mustermann', 'date_of_birth': '1990-05-01'}, format='json',
        )
        self.assertTrue(res.data['valid'])
        match = res.data['matches'][0]
        self.assertEqual(match['license_type'], 'starter')
        # data minimization: no personal fields in the response
        self.assertNotIn('name', match)
        self.assertNotIn('date_of_birth', match)

    def test_lookup_miss(self):
        _make_starter(dob='1990-05-01', submission_status='2')
        res = self.client.post(
            '/api/v1/licenses/lookup/',
            {'last_name': 'Nobody', 'date_of_birth': '1990-05-01'}, format='json',
        )
        self.assertFalse(res.data['valid'])

    def test_lookup_requires_two_identifiers(self):
        res = self.client.post(
            '/api/v1/licenses/lookup/', {'last_name': 'Mustermann'}, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lookup_requires_a_strong_identifier(self):
        # A name pair alone could be walked with a public name list.
        res = self.client.post(
            '/api/v1/licenses/lookup/',
            {'last_name': 'Mustermann', 'first_name': 'Max'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_rejects_year_out_of_range(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {self.priv}')
        self.assertEqual(
            self.client.get('/api/v1/licenses/valid/', {'year': 99999}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_lookup_rejects_year_out_of_range(self):
        res = self.client.post(
            '/api/v1/licenses/lookup/',
            {'last_name': 'Mustermann', 'date_of_birth': '1990-05-01', 'year': 99999},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lookup_needs_lookup_scope(self):
        _, key = _federal_key(name='no-lookup')
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')
        res = self.client.post(
            '/api/v1/licenses/lookup/',
            {'last_name': 'Mustermann', 'date_of_birth': '1990-05-01'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_lookup_get_is_disabled_to_keep_pii_out_of_urls(self):
        res = self.client.get(
            '/api/v1/licenses/lookup/',
            {'last_name': 'Mustermann', 'date_of_birth': '1990-05-01'},
        )
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_key_without_state_scope_is_not_unrestricted(self):
        _make_starter(state_name='NRW', state_short='NRW')
        _, key = ScopedAPIKey.objects.create_key(
            name='no-state',
            sensitive_access=True,
            allow_export_licenses=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')

        res = self.client.get('/api/v1/licenses/valid/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 0)

    def test_valid_lists_only_key_states(self):
        nrw = _make_starter(state_name='NRW', state_short='NRW')
        _make_starter(
            dob='1991-06-02',
            state_name='Hessen',
            state_short='HE',
            last_name='Fremd',
            email='f@x.de',
        )
        _, key = _scoped_key_for(nrw.gym.state, allow_export_licenses=True)
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')

        res = self.client.get('/api/v1/licenses/valid/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['id'], nrw.pk)

    def test_lookup_is_limited_to_key_states(self):
        nrw = _make_starter(state_name='NRW', state_short='NRW')
        _make_starter(
            dob='1991-06-02',
            state_name='Hessen',
            state_short='HE',
            last_name='Fremd',
            email='f@x.de',
        )
        _, key = _scoped_key_for(
            nrw.gym.state,
            sensitive_access=False,
            allow_lookup_licenses=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')

        res = self.client.post(
            '/api/v1/licenses/lookup/',
            {'last_name': 'Fremd', 'date_of_birth': '1991-06-02'}, format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['valid'])


class StateScopedApiTest(APITestCase):
    def setUp(self):
        self.bank = BankAccount.objects.create(
            owner_name='DBFV', iban='DE00', bic='X', bank_name='Bank'
        )
        self.nrw = State.objects.create(name='NRW', short_name='NRW', bank_account=self.bank)
        self.hessen = State.objects.create(
            name='Hessen', short_name='HE', bank_account=self.bank
        )

    def _auth(self, key):
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')

    def test_scoped_key_sees_only_own_state_and_gyms(self):
        Gym.objects.create(name='NRW Gym', state=self.nrw)
        Gym.objects.create(name='Hessen Gym', state=self.hessen)
        _, key = _scoped_key_for(self.nrw, sensitive_access=False)
        self._auth(key)

        states = self.client.get('/api/v1/state/')
        gyms = self.client.get('/api/v1/gym/')

        self.assertEqual([row['short_name'] for row in states.data['results']], ['NRW'])
        self.assertEqual([row['name'] for row in gyms.data['results']], ['NRW Gym'])

    def test_scoped_sensitive_key_sees_only_own_submissions(self):
        own = _make_starter(state_name='NRW2', state_short='NW2')
        _make_starter(
            dob='1991-06-02',
            state_name='Hessen2',
            state_short='HE2',
            last_name='Fremd',
            email='f@x.de',
        )
        _, key = _scoped_key_for(own.gym.state, allow_read_submissions=True)
        self._auth(key)

        res = self.client.get('/api/v1/submissionstarter/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['id'], own.pk)

    def test_scoped_write_key_cannot_write_foreign_state_data(self):
        _, key = _scoped_key_for(self.nrw, sensitive_access=False, write_allowed=True)
        self._auth(key)

        forbidden = self.client.post(
            '/api/v1/gym/', {'name': 'Falsch', 'state': self.hessen.pk}, format='json'
        )
        allowed = self.client.post(
            '/api/v1/gym/', {'name': 'Richtig', 'state': self.nrw.pk}, format='json'
        )

        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(allowed.status_code, status.HTTP_201_CREATED)

    def test_scoped_write_key_cannot_update_state_records(self):
        _, key = _scoped_key_for(self.nrw, sensitive_access=False, write_allowed=True)
        self._auth(key)

        res = self.client.patch(
            f'/api/v1/state/{self.nrw.pk}/', {'name': 'NRW geändert'}, format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_scoped_key_cannot_delete_its_own_state(self):
        # Deleting the state would cascade into every NRW gym, profile and submission.
        _, key = _scoped_key_for(self.nrw, sensitive_access=True, write_allowed=True)
        self._auth(key)

        res = self.client.delete(f'/api/v1/state/{self.nrw.pk}/')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(State.objects.filter(pk=self.nrw.pk).exists())

    def test_federal_only_models_are_hidden_from_scoped_keys(self):
        # The bank account is shared by several states, ManagerEmail receives
        # every notification nationwide and EmailCron carries outgoing mail.
        ManagerEmail.objects.create(email='boss@example.test')
        EmailCron.objects.create(subject='s', body='b', email='x@example.test')
        _, key = _scoped_key_for(self.nrw, sensitive_access=True, write_allowed=True)
        self._auth(key)

        self.assertEqual(self.client.get('/api/v1/bankaccount/').data['count'], 0)
        self.assertEqual(self.client.get('/api/v1/manageremail/').data['count'], 0)
        self.assertEqual(self.client.get('/api/v1/emailcron/').data['count'], 0)
        self.assertEqual(
            self.client.get(f'/api/v1/bankaccount/{self.bank.pk}/').status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.patch(
                f'/api/v1/bankaccount/{self.bank.pk}/', {'iban': 'DE99'}, format='json'
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.delete(f'/api/v1/bankaccount/{self.bank.pk}/').status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.post(
                '/api/v1/manageremail/', {'email': 'attacker@example.test'}, format='json'
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(BankAccount.objects.get(pk=self.bank.pk).iban, 'DE00')
        self.assertFalse(ManagerEmail.objects.filter(email='attacker@example.test').exists())

    def test_scoped_key_cannot_write_countries_or_user_profiles(self):
        country = Country.objects.create(name='Germany')
        profile_user = User.objects.create(username='nrw-member')
        profile = UserProfile.objects.get(user=profile_user)
        profile.state = self.nrw
        profile.save()
        _, key = _scoped_key_for(self.nrw, sensitive_access=True, write_allowed=True)
        self._auth(key)

        # readable within the scope ...
        self.assertEqual(self.client.get('/api/v1/country/').data['count'], 1)
        self.assertEqual(self.client.get('/api/v1/userprofile/').data['count'], 1)
        # ... but no promotion to Bundesverband, no moving out of the state,
        # no nationwide master data changes.
        promote = self.client.patch(
            f'/api/v1/userprofile/{profile.pk}/', {'type': 2}, format='json'
        )
        detach = self.client.patch(
            f'/api/v1/userprofile/{profile.pk}/', {'state': None}, format='json'
        )
        rename = self.client.patch(
            f'/api/v1/country/{country.pk}/', {'name': 'X'}, format='json'
        )
        delete = self.client.delete(f'/api/v1/country/{country.pk}/')

        for res in (promote, detach, rename, delete):
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        profile.refresh_from_db()
        self.assertEqual(profile.type, 3)
        self.assertEqual(profile.state, self.nrw)
        self.assertTrue(Country.objects.filter(pk=country.pk, name='Germany').exists())

    def test_federal_key_still_manages_bank_accounts(self):
        _, key = _federal_key(name='fed', sensitive_access=True, write_allowed=True)
        self._auth(key)

        res = self.client.get('/api/v1/bankaccount/')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)


class SubmissionIntakeApiTest(APITestCase):
    def setUp(self):
        self.bank = BankAccount.objects.create(
            owner_name='DBFV NRW', iban='DE00NRW', bic='NRW', bank_name='NRW Bank'
        )
        self.nrw = State.objects.create(
            name='NRW', short_name='NRW', email='nrw@example.test', bank_account=self.bank
        )
        self.hessen = State.objects.create(
            name='Hessen', short_name='HE', email='he@example.test', bank_account=self.bank
        )
        self.nrw_gym = Gym.objects.create(
            name='NRW Gym', email='gym@example.test', state=self.nrw
        )
        self.hessen_gym = Gym.objects.create(name='HE Gym', state=self.hessen)
        self.country = Country.objects.create(name='Germany')
        ManagerEmail.objects.create(email='boss@example.test')

    def _auth(self, key):
        self.client.credentials(HTTP_AUTHORIZATION=f'Api-Key {key}')

    def _starter_payload(self, gym_id=None):
        return {
            'gym': gym_id or self.nrw_gym.pk,
            'date_of_birth': '1990-05-01',
            'active_since': '2010',
            'last_name': 'Mustermann',
            'first_name': 'Max',
            'street': 'Weg',
            'house_nr': '1',
            'zip_code': 12345,
            'city': 'Koeln',
            'tel_number': '0123',
            'email': 'max@example.test',
            'nationality': self.country.pk,
            'height': 180,
            'weight': '80.00',
            'category': '1',
            'terms_and_conditions': True,
            'data_protection': True,
            'submission_last_year': False,
            'external_reference': 'NRW-ORDER-1',
            'championships': ['NRW Meisterschaft'],
            'payment': {
                'status': 'paid',
                'method': 'dfvnrw',
                'reference': 'NRW-2026-1',
                'amount_cents': 9000,
                'received_at': '2026-09-16T12:00:00+02:00',
                'note': 'Bezahlt im NRW-Frontend',
            },
        }

    def _gym_payload(self):
        return {
            'state': self.nrw.pk,
            'name': 'Neuer NRW Verein',
            'owner': 'Erika Beispiel',
            'founded': '2020-01-01',
            'street': 'Vereinsweg',
            'zip_code': 54321,
            'city': 'Bonn',
            'tel_number': '0228',
            'email': 'verein@example.test',
            'external_reference': 'NRW-GYM-1',
        }

    def test_starter_submission_with_payment_saves_and_sends_notifications(self):
        _, key = _scoped_key_for(
            self.nrw,
            allow_submit_starter=True,
            allow_register_payments=True,
        )
        self._auth(key)

        res = self.client.post(
            '/api/v1/submissions/starter/', self._starter_payload(), format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        submission = SubmissionStarter.objects.get(pk=res.data['id'])
        self.assertTrue(submission.created_via_api)
        self.assertEqual(submission.api_key_prefix, key.split('.', 1)[0])
        self.assertEqual(submission.payment_status, 'paid')
        self.assertEqual(submission.payment_method, 'dfvnrw')
        self.assertEqual(submission.payment_reference, 'NRW-2026-1')
        self.assertEqual(submission.payment_amount_cents, 9000)
        self.assertEqual(submission.external_reference, 'NRW-ORDER-1')
        self.assertFalse(res.data['reused'])
        recipients = {recipient for message in mail.outbox for recipient in message.to}
        self.assertIn('boss@example.test', recipients)
        self.assertIn('nrw@example.test', recipients)
        self.assertIn('gym@example.test', recipients)
        self.assertIn('max@example.test', recipients)
        self.assertTrue(any('NRW-2026-1' in message.body for message in mail.outbox))
        self.assertTrue(any('90,00 €' in message.body for message in mail.outbox))

    def test_repeated_external_reference_reuses_existing_submission(self):
        _, key = _scoped_key_for(
            self.nrw,
            allow_submit_starter=True,
            allow_register_payments=True,
        )
        self._auth(key)
        payload = self._starter_payload()

        first = self.client.post('/api/v1/submissions/starter/', payload, format='json')
        second = self.client.post('/api/v1/submissions/starter/', payload, format='json')

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data['id'], second.data['id'])
        self.assertTrue(second.data['reused'])
        self.assertEqual(SubmissionStarter.objects.count(), 1)

    def test_paid_payment_requires_reference_and_amount(self):
        _, key = _scoped_key_for(
            self.nrw,
            allow_submit_starter=True,
            allow_register_payments=True,
        )
        self._auth(key)
        payload = self._starter_payload()
        payload['external_reference'] = 'NRW-ORDER-BAD-PAYMENT'
        payload['payment'] = {'status': 'paid', 'method': 'dfvnrw'}

        res = self.client.post('/api/v1/submissions/starter/', payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(SubmissionStarter.objects.exists())

    def test_payment_requires_explicit_payment_permission(self):
        _, key = _scoped_key_for(self.nrw, allow_submit_starter=True)
        self._auth(key)

        res = self.client.post(
            '/api/v1/submissions/starter/', self._starter_payload(), format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(SubmissionStarter.objects.exists())

    def test_paid_amount_must_match_fee(self):
        _, key = _scoped_key_for(
            self.nrw,
            allow_submit_starter=True,
            allow_register_payments=True,
        )
        self._auth(key)
        payload = self._starter_payload()
        payload['payment']['amount_cents'] = 1

        res = self.client.post('/api/v1/submissions/starter/', payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount_cents', res.data['payment'])
        self.assertFalse(SubmissionStarter.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_payment_received_at_must_not_be_in_the_future(self):
        _, key = _scoped_key_for(
            self.nrw,
            allow_submit_starter=True,
            allow_register_payments=True,
        )
        self._auth(key)
        payload = self._starter_payload()
        payload['payment']['received_at'] = '2099-01-01T00:00:00+00:00'

        res = self.client.post('/api/v1/submissions/starter/', payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(SubmissionStarter.objects.exists())

    def test_api_submissions_belong_to_technical_key_user_not_to_web_accounts(self):
        web_user = User.objects.create_user(
            'max', email='max@example.test', password='pw', is_superuser=True
        )
        _, key = _scoped_key_for(self.nrw, allow_submit_starter=True)
        self._auth(key)
        payload = self._starter_payload()
        payload.pop('payment')

        res = self.client.post('/api/v1/submissions/starter/', payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        submission = SubmissionStarter.objects.get(pk=res.data['id'])
        self.assertNotEqual(submission.user, web_user)
        self.assertEqual(submission.user.username, f"api-{key.split('.', 1)[0]}")
        self.assertFalse(submission.user.is_active)
        self.assertFalse(submission.user.has_usable_password())
        self.assertEqual(submission.user.email, '')
        # applicant data stays on the submission only
        self.assertEqual(submission.email, 'max@example.test')

    def test_license_pdf_goes_to_the_applicant_not_the_technical_user(self):
        _, key = _scoped_key_for(self.nrw, allow_submit_starter=True)
        self._auth(key)
        payload = self._starter_payload()
        payload.pop('payment')
        res = self.client.post('/api/v1/submissions/starter/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mail.outbox.clear()

        submission = SubmissionStarter.objects.get(pk=res.data['id'])
        submission.send_pdf_email()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['max@example.test'])

    def test_designated_use_is_plain_text(self):
        _, key = _scoped_key_for(self.nrw, allow_submit_starter=True)
        self._auth(key)
        payload = self._starter_payload()
        payload.pop('payment')

        res = self.client.post('/api/v1/submissions/starter/', payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('<br>', res.data['designated_use'])
        self.assertIn('Mustermann, Max', res.data['designated_use'])

    def test_duplicate_reference_is_rejected_by_the_database(self):
        first = _make_starter(state_name='NRW3', state_short='NW3')
        first.created_via_api = True
        first.api_key_prefix = 'ABCDEFGH'
        first.external_reference = 'NRW-ORDER-X'
        first.save()

        with self.assertRaises(IntegrityError), transaction.atomic():
            SubmissionStarter.objects.create(
                user=first.user, date_of_birth='1990-05-01', active_since='2010',
                last_name='Doppelt', first_name='Max', street='Weg', house_nr='1',
                zip_code=12345, city='Köln', tel_number='0', email='d@x.de',
                nationality=first.nationality, height=180, weight=80, category='1',
                terms_and_conditions=True, gym=first.gym, created_via_api=True,
                api_key_prefix='ABCDEFGH', external_reference='NRW-ORDER-X',
            )

        # web submissions carry no reference and never collide with each other
        self.assertIsNone(_make_starter(state_name='NRW4', state_short='NW4').external_reference)
        self.assertIsNone(_make_starter(state_name='NRW5', state_short='NW5').external_reference)

    def test_state_scope_blocks_foreign_gym_submission(self):
        _, key = _scoped_key_for(
            self.nrw,
            allow_submit_starter=True,
            allow_register_payments=True,
        )
        self._auth(key)

        res = self.client.post(
            '/api/v1/submissions/starter/',
            self._starter_payload(gym_id=self.hessen_gym.pk),
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(SubmissionStarter.objects.exists())

    def test_gym_submission_creates_inactive_gym_like_webflow(self):
        _, key = _scoped_key_for(self.nrw, allow_submit_gym=True)
        self._auth(key)

        res = self.client.post(
            '/api/v1/submissions/gym/', self._gym_payload(), format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_gym = Gym.objects.get(name='Neuer NRW Verein')
        self.assertFalse(new_gym.is_active)
        self.assertEqual(new_gym.state, self.nrw)
        recipients = {recipient for message in mail.outbox for recipient in message.to}
        self.assertIn('boss@example.test', recipients)
        self.assertIn('nrw@example.test', recipients)
        self.assertIn('verein@example.test', recipients)

    def test_judge_submission_without_email_sends_notifications(self):
        # Judge e-mail is optional; a None recipient used to break send_emails().
        _, key = _scoped_key_for(self.nrw, allow_submit_judge=True)
        self._auth(key)

        res = self.client.post(
            '/api/v1/submissions/judge/',
            {
                'last_name': 'Richter', 'first_name': 'Rita', 'street': 'Weg 1',
                'zip_code': 12345, 'city': 'Koeln', 'state': self.nrw.pk,
                'tel_number': '0123', 'data_protection': True,
                'external_reference': 'NRW-JUDGE-1',
            },
            format='json',
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipients = {recipient for message in mail.outbox for recipient in message.to}
        self.assertIn('boss@example.test', recipients)
        self.assertIn('nrw@example.test', recipients)
        self.assertNotIn(None, recipients)

    def test_capabilities_and_options_are_state_scoped(self):
        _, key = _scoped_key_for(self.nrw, allow_submit_starter=True)
        self._auth(key)

        capabilities = self.client.get('/api/v1/capabilities/')
        options = self.client.get('/api/v1/submissions/options/')

        self.assertEqual(capabilities.status_code, status.HTTP_200_OK)
        self.assertTrue(capabilities.data['permissions']['submit_starter'])
        self.assertFalse(capabilities.data['permissions']['register_payments'])
        self.assertFalse(capabilities.data['permissions']['lookup_licenses'])
        self.assertFalse(capabilities.data['permissions']['export_licenses'])
        self.assertEqual([state['short_name'] for state in capabilities.data['states']], ['NRW'])
        self.assertEqual([gym['name'] for gym in options.data['gyms']], ['NRW Gym'])


class AuditLogTest(APITestCase):
    def test_denied_request_logged_without_secret_or_query(self):
        _, key = ScopedAPIKey.objects.create_key(name='audit')
        with self.assertLogs('dbfv.audit', level='INFO') as cm:
            # valid key + a search term that must NOT appear in the audit line
            self.client.get(
                '/api/v1/country/', {'search': 'TOPSECRETNAME'},
                HTTP_AUTHORIZATION=f'Api-Key {key}',
            )
            # no key -> 403, logged at WARNING
            self.client.get('/api/v1/country/')
        joined = '\n'.join(cm.output)
        self.assertIn('path=/api/v1/country/', joined)
        self.assertIn('status=403', joined)
        self.assertNotIn('TOPSECRETNAME', joined)  # query/search data never logged
        self.assertNotIn(key.split('.', 1)[1], joined)  # secret never logged

        rows = list(APIAccessLog.objects.order_by('created_at'))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].key_prefix, key.split('.', 1)[0])
        self.assertEqual(rows[0].path, '/api/v1/country/')
        self.assertEqual(rows[0].status_code, status.HTTP_200_OK)
        self.assertEqual(rows[1].key_prefix, '-')
        self.assertEqual(rows[1].status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn('TOPSECRETNAME', rows[0].path)
        self.assertNotIn(key.split('.', 1)[1], rows[0].path)

    def test_logged_key_prefix_is_bounded(self):
        self.client.get('/api/v1/country/', HTTP_AUTHORIZATION='Api-Key ' + 'A' * 300 + '.x')
        row = APIAccessLog.objects.get()
        self.assertEqual(row.key_prefix, 'A' * 8)
        self.assertEqual(row.status_code, status.HTTP_403_FORBIDDEN)
