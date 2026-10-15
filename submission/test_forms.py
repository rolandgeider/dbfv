"""Regression coverage for browser form ownership and create/edit flows."""

from html.parser import HTMLParser
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from submission.models import (
    BankAccount,
    Country,
    Gym,
    State,
    SubmissionInternational,
    SubmissionStarter,
)


class FormControls(HTMLParser):
    """Collect controls using HTML's enclosing-form or explicit form= owner."""

    def __init__(self, html):
        super().__init__()
        self.forms = []
        self.controls = []
        self.current_form = None
        self.application_form = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.current_form = attrs.get('id', f'form-{len(self.forms)}')
            self.forms.append(self.current_form)
        if tag in ('input', 'select', 'textarea', 'button'):
            owner = attrs.get('form', self.current_form)
            self.controls.append((owner, attrs))
            if 'wizard-submit' in attrs.get('class', '').split():
                self.application_form = owner

    def handle_endtag(self, tag):
        if tag == 'form':
            self.current_form = None

    def submitted_values(self, values):
        """Only send entered values that the browser associates with the form."""
        return {
            attrs['name']: values[attrs['name']]
            for owner, attrs in self.controls
            if owner == self.application_form
            and owner in self.forms
            and attrs.get('name') in values
            and 'disabled' not in attrs
        }


class SubmissionWizardTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        bank = BankAccount.objects.create(
            pk=1, iban='DE89370400440532013000', bic='COBADEFFXXX', bank_name='Testbank'
        )
        cls.state = State.objects.create(name='Testverband', short_name='TV', bank_account=bank)
        cls.gym = Gym.objects.create(name='Teststudio', city='Berlin', state=cls.state)
        cls.country = Country.objects.create(name='Deutschland')
        cls.user = User.objects.create_user(username='wizard-user', email='athlete@example.com')
        cls.user.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='submission',
            codename__in=('add_submissionstarter', 'add_submissioninternational'),
        ))

    def setUp(self):
        self.client.force_login(self.user)

    def values(self, international=False):
        values = {
            'gym': str(self.gym.pk),
            'first_name': 'Erika',
            'last_name': 'Mustermann',
            'date_of_birth': '1990-01-02',
            'nationality': str(self.country.pk),
            'street': 'Teststraße',
            'zip_code': '10115',
            'city': 'Berlin',
            'tel_number': '0301234567',
            'email': 'athlete@example.com',
            'height': '175',
            'weight': '70.00',
            'category': '1',
            'terms_and_conditions': 'on',
        }
        if international:
            values.update(
                championship='Testmeisterschaft', championship_date='2027-06-01',
                best_placement='1. Platz DM 2025', requirements_ack='on',
            )
        else:
            values.update(active_since='2018', house_nr='12', data_protection='on')
        return values

    def create_submission(self, international=False):
        values = self.values(international)
        for name in ('data_protection', 'requirements_ack'):
            values.pop(name, None)
        if international:
            values.pop('terms_and_conditions')
        else:
            values['terms_and_conditions'] = True
        values['gym'] = self.gym
        values['nationality'] = self.country
        model = SubmissionInternational if international else SubmissionStarter
        return model.objects.create(user=self.user, **values)

    def assert_wizard(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-wizard-next')
        self.assertContains(response, 'data-wizard-back')
        self.assertContains(response, self.state.name)
        self.assertContains(response, self.gym.name)
        controls = FormControls(response.content.decode())
        self.assertIn(controls.application_form, controls.forms)
        return controls

    def test_international_create_submits_prerequisites_with_form(self):
        url = reverse('submission-international-add')
        controls = self.assert_wizard(self.client.get(url))
        payload = controls.submitted_values(self.values(international=True))
        self.assertEqual(payload['requirements_ack'], 'on')
        with patch.object(SubmissionInternational, 'send_emails'):
            response = self.client.post(url, payload)
        self.assertRedirects(response, reverse('bank-account-view'), fetch_redirect_response=False)
        self.assertEqual(SubmissionInternational.objects.get().user, self.user)

    def test_international_create_requires_prerequisites_and_restores_error(self):
        values = self.values(international=True)
        values.pop('requirements_ack')
        response = self.client.post(reverse('submission-international-add'), values)
        controls = self.assert_wizard(response)
        self.assertFormError(response.context['form'], 'requirements_ack',
                             'Bitte bestätigen Sie die Voraussetzungen.')
        self.assertEqual(controls.submitted_values({'requirements_ack': 'on'}),
                         {'requirements_ack': 'on'})
        self.assertFalse(SubmissionInternational.objects.exists())

    def test_starter_create_includes_legal_modal_and_submits(self):
        url = reverse('submission-add', kwargs={'type': 'starter'})
        response = self.client.get(url)
        controls = self.assert_wizard(response)
        self.assertContains(response, 'id="legalModal"')
        self.assertContains(response, 'id="legalModalBody"')
        with patch.object(SubmissionStarter, 'send_emails'):
            response = self.client.post(url, controls.submitted_values(self.values()))
        self.assertRedirects(response, reverse('bank-account-view'), fetch_redirect_response=False)
        self.assertEqual(SubmissionStarter.objects.get().user, self.user)

    def test_starter_edit_has_wizard_legal_modal_and_saves(self):
        submission = self.create_submission()
        url = reverse('submission-edit', kwargs={'pk': submission.pk})
        response = self.client.get(url)
        controls = self.assert_wizard(response)
        self.assertTemplateUsed(response, 'submission/starter/create.html')
        self.assertContains(response, 'Starterlizenz bearbeiten')
        self.assertContains(response, 'id="legalModal"')
        self.assertContains(response, 'id="legalModalBody"')
        self.assertNotContains(response, 'Lizenzgebühr')
        values = self.values()
        values['first_name'] = 'Eva'
        response = self.client.post(url, controls.submitted_values(values))
        self.assertRedirects(response, submission.get_absolute_url(), fetch_redirect_response=False)
        submission.refresh_from_db()
        self.assertEqual(submission.first_name, 'Eva')
        self.assertEqual(SubmissionStarter.objects.count(), 1)

    def test_starter_edit_still_requires_both_consents(self):
        submission = self.create_submission()
        values = self.values()
        values.pop('terms_and_conditions')
        values.pop('data_protection')
        response = self.client.post(reverse('submission-edit', kwargs={'pk': submission.pk}), values)
        self.assertEqual(response.status_code, 200)
        self.assertIn('terms_and_conditions', response.context['form'].errors)
        self.assertIn('data_protection', response.context['form'].errors)

    def test_international_edit_has_prerequisites_and_saves(self):
        submission = self.create_submission(international=True)
        url = reverse('submission-international-edit', kwargs={'pk': submission.pk})
        response = self.client.get(url)
        controls = self.assert_wizard(response)
        self.assertTemplateUsed(response, 'submission/international/create.html')
        self.assertContains(response, 'Internationalen Antrag bearbeiten')
        self.assertContains(response, 'Voraussetzungen &amp; Anmeldebestimmungen')
        self.assertNotContains(response, 'Bearbeitungsgebühr')
        values = self.values(international=True)
        values['first_name'] = 'Eva'
        payload = controls.submitted_values(values)
        self.assertEqual(payload['requirements_ack'], 'on')
        response = self.client.post(url, payload)
        self.assertRedirects(response, submission.get_absolute_url(), fetch_redirect_response=False)
        submission.refresh_from_db()
        self.assertEqual(submission.first_name, 'Eva')
        self.assertEqual(SubmissionInternational.objects.count(), 1)

    def test_international_edit_still_requires_prerequisites(self):
        submission = self.create_submission(international=True)
        values = self.values(international=True)
        values.pop('requirements_ack')
        response = self.client.post(
            reverse('submission-international-edit', kwargs={'pk': submission.pk}), values
        )
        self.assert_wizard(response)
        self.assertIn('requirements_ack', response.context['form'].errors)
