"""Mail failures and approval transitions must preserve application state."""

from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from api.tests import _make_starter
from submission import test_forms as form_fixtures
from submission.models import Gym, SubmissionGym, SubmissionJudge, SubmissionStarter


class WebSubmissionTransactionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        form_fixtures.SubmissionWizardTest.setUpTestData.__func__(cls)
        cls.user.user_permissions.add(Permission.objects.get(codename='add_submissiongym'))

    def setUp(self):
        self.client.force_login(self.user)

    values = form_fixtures.SubmissionWizardTest.values

    def test_starter_mail_failure_rolls_back_and_retry_creates_one_application(self):
        url = reverse('submission-add', kwargs={'type': 'starter'})
        with patch('submission.models.mail.send_mail', side_effect=OSError('SMTP unavailable')):
            with self.assertRaises(OSError):
                self.client.post(url, self.values())
        self.assertFalse(SubmissionStarter.objects.exists())
        response = self.client.post(url, self.values())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SubmissionStarter.objects.count(), 1)
        self.assertEqual(self.client.session['submission-fee'], SubmissionStarter.FEE)

    def test_gym_mail_failure_rolls_back_both_records_and_retry_succeeds(self):
        url = reverse('submission-studio-add')
        payload = {
            'state': self.state.pk, 'name': 'New gym', 'owner': 'Owner',
            'founded': '2020-01-01', 'street': 'Street', 'zip_code': 12345,
            'city': 'City', 'tel_number': '0123', 'email': 'gym@example.test',
        }
        with patch('submission.models.mail.send_mail', side_effect=OSError('SMTP unavailable')):
            with self.assertRaises(OSError):
                self.client.post(url, payload)
        self.assertFalse(SubmissionGym.objects.exists())
        self.assertFalse(Gym.objects.filter(name='New gym').exists())
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        submission = SubmissionGym.objects.get()
        self.assertIsNotNone(submission.gym_id)
        self.assertFalse(submission.gym.is_active)
        self.assertEqual(Gym.objects.filter(name='New gym').count(), 1)


class ApprovalPDFTest(TestCase):
    def setUp(self):
        self.starter = _make_starter(submission_status='1')
        self.technical_user = User.objects.create_user('api:test', is_active=False)
        self.judge = SubmissionJudge.objects.create(
            user=self.technical_user, first_name='Test', last_name='Judge',
            state=self.starter.gym.state, street='Street', zip_code=12345,
            city='City', tel_number='0123',
        )

    def test_judge_without_email_is_not_marked_sent_and_can_retry_after_adding_email(self):
        self.judge.submission_status = self.judge.SUBMISSION_STATUS_BEWILLIGT
        self.judge.save(update_fields=['submission_status'])
        self.judge.refresh_from_db()
        self.assertFalse(self.judge.pdf_sent)
        self.assertEqual(len(mail.outbox), 0)
        self.judge.email = 'judge@example.test'
        self.judge.save(update_fields=['email'])
        self.judge.refresh_from_db()
        self.assertTrue(self.judge.pdf_sent)
        self.assertEqual(mail.outbox[0].to, ['judge@example.test'])
        self.assertEqual(len(mail.outbox), 1)

    def test_approval_tracks_delivery_without_resending_on_unrelated_saves(self):
        for submission in (self.starter, self.judge):
            with self.subTest(model=type(submission).__name__):
                submission.email = 'applicant@example.test'
                submission.submission_status = submission.SUBMISSION_STATUS_BEWILLIGT
                mail.outbox.clear()
                submission.save(update_fields=['email', 'submission_status'])
                submission.refresh_from_db()
                self.assertTrue(submission.pdf_sent)
                self.assertEqual(len(mail.outbox), 1)
                submission.first_name = 'Changed'
                submission.save()
                submission.save(update_fields=['first_name'])
                self.assertEqual(len(mail.outbox), 1)
                submission.submission_status = submission.SUBMISSION_STATUS_ABGELEHNT
                submission.save(update_fields=['submission_status'])
                submission.submission_status = submission.SUBMISSION_STATUS_BEWILLIGT
                submission.save(update_fields=['submission_status'])
                self.assertEqual(len(mail.outbox), 2)

    def test_zero_deliveries_does_not_mark_pdf_sent(self):
        self.starter.submission_status = self.starter.SUBMISSION_STATUS_BEWILLIGT
        with patch('submission.models.EmailMultiAlternatives.send', return_value=0):
            self.starter.save()
        self.starter.refresh_from_db()
        self.assertFalse(self.starter.pdf_sent)

    def test_partial_unrelated_save_does_not_send_unpersisted_approval(self):
        self.starter.submission_status = self.starter.SUBMISSION_STATUS_BEWILLIGT
        self.starter.first_name = 'Changed'
        self.starter.save(update_fields=['first_name'])
        self.starter.refresh_from_db()
        self.assertEqual(self.starter.submission_status, self.starter.SUBMISSION_STATUS_EINGEGANGEN)
        self.assertFalse(self.starter.pdf_sent)
        self.assertEqual(len(mail.outbox), 0)

    def test_explicit_resend_updates_delivery_flag(self):
        admin = User.objects.create_user('pdf-manager', is_superuser=True, is_staff=True)
        self.client.force_login(admin)
        for submission, route in ((self.starter, 'submission-resend-pdf'),
                                  (self.judge, 'submission-judge-resend-pdf')):
            with self.subTest(model=type(submission).__name__):
                type(submission).objects.filter(pk=submission.pk).update(
                    submission_status=submission.SUBMISSION_STATUS_BEWILLIGT,
                    email='recipient@example.test', pdf_sent=False,
                )
                mail.outbox.clear()
                response = self.client.post(reverse(route, kwargs={'pk': submission.pk}))
                self.assertEqual(response.status_code, 302)
                submission.refresh_from_db()
                self.assertTrue(submission.pdf_sent)
                self.assertEqual(len(mail.outbox), 1)
