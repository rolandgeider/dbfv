"""Dedicated submission intake API.

These endpoints intentionally do not expose generic CRUD writes. They create
domain submissions through the same notification path as the web forms.
"""

# Standard Library
from datetime import timedelta

# Third Party
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone

# dbfv
from api.access import api_key_from_request, filter_queryset_for_request
from submission.models import (
    Country,
    Gym,
    State,
    SubmissionGym,
    SubmissionInternational,
    SubmissionJudge,
    SubmissionStarter,
)


def _api_user(api_key):
    """
    Return the technical user that owns submissions created with ``api_key``.

    Submissions are deliberately *not* attached to an existing web account
    with the applicant's e-mail address: that would hand the submission (and
    its personal data) to whoever registered that address first, and a judge
    submission without e-mail would even match accounts with an empty e-mail.
    The applicant's contact data lives only in the submission itself.
    """
    user, _ = User.objects.get_or_create(
        username=f'api-{api_key.prefix}',
        defaults={
            'first_name': 'API',
            'last_name': api_key.name,
            'email': '',
            'is_active': False,
            'password': make_password(None),  # unusable
        },
    )
    return user


def _state_allowed(api_key, state_id):
    if api_key.has_federal_access():
        return True
    return state_id in api_key.allowed_state_ids()


def _state_ids_for_key(api_key):
    if api_key.has_federal_access():
        return None
    return api_key.allowed_state_ids()


class PaymentSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[choice[0] for choice in SubmissionStarter.PAYMENT_STATUS])
    method = serializers.CharField(required=False, allow_blank=True, max_length=40)
    reference = serializers.CharField(required=False, allow_blank=True, max_length=120)
    amount_cents = serializers.IntegerField(required=False, min_value=0)
    received_at = serializers.DateTimeField(required=False)
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_received_at(self, value):
        if value > timezone.now() + timedelta(minutes=5):
            raise serializers.ValidationError('Zahlungszeitpunkt darf nicht in der Zukunft liegen.')
        return value

    def validate(self, attrs):
        if attrs.get('status') == SubmissionStarter.PAYMENT_STATUS_PAID:
            if not attrs.get('reference'):
                raise serializers.ValidationError({
                    'reference': 'Bei bezahlten Anträgen ist eine Zahlungsreferenz Pflicht.'
                })
            if attrs.get('amount_cents') in (None, 0):
                raise serializers.ValidationError({
                    'amount_cents': 'Bei bezahlten Anträgen ist ein Betrag größer 0 Pflicht.'
                })
        return attrs


class _ExternalReferenceMixin(serializers.Serializer):
    external_reference = serializers.CharField(max_length=120, write_only=True)

    def validate_external_reference(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Externe Referenz ist Pflicht.')
        return value


class StarterSubmissionSerializer(_ExternalReferenceMixin, serializers.ModelSerializer):
    data_protection = serializers.BooleanField(write_only=True)
    championships = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True, write_only=True
    )
    payment = PaymentSerializer(required=False, write_only=True)

    class Meta:
        model = SubmissionStarter
        fields = [
            'gym', 'date_of_birth', 'active_since', 'last_name', 'first_name',
            'street', 'house_nr', 'zip_code', 'city', 'tel_number', 'email',
            'nationality', 'height', 'weight', 'category', 'terms_and_conditions',
            'submission_last_year', 'data_protection', 'championships', 'payment',
            'external_reference',
        ]

    def validate_data_protection(self, value):
        if not value:
            raise serializers.ValidationError('Datenschutzbestimmung muss bestätigt sein.')
        return value


class InternationalSubmissionSerializer(_ExternalReferenceMixin, serializers.ModelSerializer):
    terms_and_conditions = serializers.BooleanField(write_only=True)
    payment = PaymentSerializer(required=False, write_only=True)

    class Meta:
        model = SubmissionInternational
        fields = [
            'gym', 'date_of_birth', 'last_name', 'first_name', 'street', 'zip_code',
            'city', 'tel_number', 'email', 'nationality', 'height', 'weight',
            'category', 'championship', 'championship_date', 'best_placement',
            'terms_and_conditions', 'payment', 'external_reference',
        ]

    def validate_terms_and_conditions(self, value):
        if not value:
            raise serializers.ValidationError('Regeln des DBFV e.V. müssen bestätigt sein.')
        return value


class GymSubmissionSerializer(_ExternalReferenceMixin, serializers.ModelSerializer):
    payment = PaymentSerializer(required=False, write_only=True)

    class Meta:
        model = SubmissionGym
        fields = [
            'state', 'name', 'owner', 'founded', 'street', 'zip_code', 'city',
            'tel_number', 'email', 'payment', 'external_reference',
        ]


class JudgeSubmissionSerializer(_ExternalReferenceMixin, serializers.ModelSerializer):
    data_protection = serializers.BooleanField(write_only=True)
    payment = PaymentSerializer(required=False, write_only=True)

    class Meta:
        model = SubmissionJudge
        fields = [
            'last_name', 'first_name', 'street', 'zip_code', 'city', 'state',
            'tel_number', 'email', 'data_protection', 'payment', 'external_reference',
        ]

    def validate_data_protection(self, value):
        if not value:
            raise serializers.ValidationError('Datenschutzbestimmung muss bestätigt sein.')
        return value


class CreatedSubmissionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    license_type = serializers.CharField()
    status = serializers.CharField()
    payment_status = serializers.CharField()
    bank_account_id = serializers.IntegerField()
    fee = serializers.IntegerField()
    designated_use = serializers.CharField()
    external_reference = serializers.CharField()
    reused = serializers.BooleanField()


class StateOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    short_name = serializers.CharField()


class GymOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    state_id = serializers.IntegerField()


class CountryOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class ChoiceOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class CapabilitiesSerializer(serializers.Serializer):
    key_prefix = serializers.CharField()
    federal_access = serializers.BooleanField()
    states = StateOptionSerializer(many=True)
    permissions = serializers.DictField(child=serializers.BooleanField())


class SubmissionOptionsSerializer(serializers.Serializer):
    states = StateOptionSerializer(many=True)
    gyms = GymOptionSerializer(many=True)
    countries = CountryOptionSerializer(many=True)
    starter_categories = ChoiceOptionSerializer(many=True)
    payment_statuses = ChoiceOptionSerializer(many=True)


class _SubmissionCreateView(APIView):
    serializer_class = None
    model = None
    permission_flag = None
    api_submission_permission_flag = None
    state_field = None
    license_type = None
    form_only_fields = ()

    def _state_id(self, data):
        if self.state_field == 'gym':
            return data['gym'].state_id
        return data['state'].pk

    def _build_extra_data(self, validated, payment_data):
        extra_data = {'source': 'api'}
        if 'championships' in validated:
            extra_data['championships'] = validated.pop('championships') or []
        if payment_data:
            extra_data['payment'] = payment_data
        return extra_data

    def _apply_payment(self, submission, payment_data):
        if not payment_data:
            return
        fee_cents = submission.FEE * 100
        if (
            payment_data['status'] == submission.PAYMENT_STATUS_PAID
            and payment_data.get('amount_cents') != fee_cents
        ):
            raise serializers.ValidationError({
                'payment': {
                    'amount_cents': [
                        f'Bei bezahlten Anträgen muss der Betrag der Gebühr '
                        f'von {submission.FEE} € entsprechen ({fee_cents} Cent).'
                    ]
                }
            })
        submission.payment_status = payment_data['status']
        submission.payment_method = payment_data.get('method', '')
        submission.payment_reference = payment_data.get('reference', '')
        submission.payment_amount_cents = payment_data.get('amount_cents')
        submission.payment_received_at = payment_data.get('received_at') or timezone.now()
        submission.payment_note = payment_data.get('note', '')

    def _response_payload(self, submission, reused=False):
        return {
            'id': submission.pk,
            'license_type': self.license_type,
            'status': submission.get_submission_status_display(),
            'payment_status': submission.get_payment_status_display(),
            'bank_account_id': submission.get_bank_account(),
            'fee': submission.FEE,
            'designated_use': submission.get_bank_designated_use_text(),
            'external_reference': submission.external_reference,
            'reused': reused,
        }

    def _after_submission_saved(self, submission):
        return submission

    def post(self, request):
        api_key = api_key_from_request(request)
        if not api_key or not getattr(api_key, self.permission_flag):
            return Response(
                {'detail': 'Dieser API-Key darf diese Antragsart nicht anlegen.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = dict(serializer.validated_data)
        payment_data = validated.pop('payment', None)
        external_reference = validated.pop('external_reference')
        if payment_data and not api_key.allow_register_payments:
            return Response(
                {'payment': ['Dieser API-Key darf keine Zahlungen registrieren.']},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Form-only confirmation fields are validated above and not model fields.
        for field in self.form_only_fields:
            validated.pop(field, None)

        state_id = self._state_id(validated)
        if not _state_allowed(api_key, state_id):
            return Response(
                {'detail': 'Dieser API-Key darf keine Anträge für diesen Landesverband anlegen.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        extra_data = self._build_extra_data(validated, payment_data)
        existing = self._existing(api_key, external_reference)
        if existing is not None:
            return self._reused_response(api_key, existing)

        try:
            # One transaction: technical user, submission, gym (studio
            # applications) and notification mails either all succeed or
            # nothing is stored. A mail failure therefore surfaces as 500 and
            # the client may safely retry with the same external_reference.
            with transaction.atomic():
                submission = self.model(
                    **validated,
                    user=_api_user(api_key),
                    created_via_api=True,
                    api_key_prefix=api_key.prefix,
                    external_reference=external_reference,
                )
                self._apply_payment(submission, payment_data)
                submission.save()
                submission = self._after_submission_saved(submission)
                submission.send_emails(extra_data)
        except IntegrityError:
            # Lost the race against a parallel retry with the same reference:
            # the unique constraint (api_key_prefix, external_reference) held.
            existing = self._existing(api_key, external_reference)
            if existing is None:
                raise
            return self._reused_response(api_key, existing)

        return Response(self._response_payload(submission), status=status.HTTP_201_CREATED)

    def _existing(self, api_key, external_reference):
        return self.model.objects.filter(
            created_via_api=True,
            api_key_prefix=api_key.prefix,
            external_reference=external_reference,
        ).first()

    def _reused_response(self, api_key, existing):
        if not _state_allowed(api_key, self._state_id_from_submission(existing)):
            return Response(
                {'detail': 'Bestehender Antrag liegt außerhalb des erlaubten Landesverbands.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(self._response_payload(existing, reused=True), status=status.HTTP_200_OK)

    def _state_id_from_submission(self, submission):
        if self.state_field == 'gym':
            return submission.gym.state_id
        return submission.state_id


class StarterSubmissionCreateView(_SubmissionCreateView):
    serializer_class = StarterSubmissionSerializer
    model = SubmissionStarter
    permission_flag = 'allow_submit_starter'
    api_submission_permission_flag = 'allow_submit_starter'
    state_field = 'gym'
    license_type = 'starter'
    form_only_fields = ('data_protection',)

    @extend_schema(request=StarterSubmissionSerializer, responses=CreatedSubmissionSerializer)
    def post(self, request):
        return super().post(request)


class InternationalSubmissionCreateView(_SubmissionCreateView):
    serializer_class = InternationalSubmissionSerializer
    model = SubmissionInternational
    permission_flag = 'allow_submit_international'
    api_submission_permission_flag = 'allow_submit_international'
    state_field = 'gym'
    license_type = 'international'
    form_only_fields = ('terms_and_conditions',)

    @extend_schema(request=InternationalSubmissionSerializer, responses=CreatedSubmissionSerializer)
    def post(self, request):
        return super().post(request)


class GymSubmissionCreateView(_SubmissionCreateView):
    serializer_class = GymSubmissionSerializer
    model = SubmissionGym
    permission_flag = 'allow_submit_gym'
    api_submission_permission_flag = 'allow_submit_gym'
    state_field = 'state'
    license_type = 'studio'

    @extend_schema(request=GymSubmissionSerializer, responses=CreatedSubmissionSerializer)
    def post(self, request):
        return super().post(request)

    def _after_submission_saved(self, submission):
        gym = Gym.objects.create(
            name=submission.name,
            email=submission.email,
            state=submission.state,
            owner='',
            zip_code=submission.zip_code,
            city=submission.city,
            street=submission.street,
            is_active=False,
        )
        submission.gym = gym
        submission.save(update_fields=['gym'])
        return submission


class JudgeSubmissionCreateView(_SubmissionCreateView):
    serializer_class = JudgeSubmissionSerializer
    model = SubmissionJudge
    permission_flag = 'allow_submit_judge'
    api_submission_permission_flag = 'allow_submit_judge'
    state_field = 'state'
    license_type = 'judge'
    form_only_fields = ('data_protection',)

    @extend_schema(request=JudgeSubmissionSerializer, responses=CreatedSubmissionSerializer)
    def post(self, request):
        return super().post(request)


class CapabilitiesView(APIView):
    @extend_schema(responses=CapabilitiesSerializer)
    def get(self, request):
        api_key = api_key_from_request(request)
        state_ids = _state_ids_for_key(api_key)
        states = State.objects.all().order_by('name')
        if state_ids is not None:
            states = states.filter(pk__in=state_ids)
        return Response({
            'key_prefix': api_key.prefix,
            'federal_access': api_key.federal_access,
            'states': [
                {'id': state.pk, 'name': state.name, 'short_name': state.short_name}
                for state in states
            ],
            'permissions': {
                'submit_starter': api_key.allow_submit_starter,
                'submit_international': api_key.allow_submit_international,
                'submit_gym': api_key.allow_submit_gym,
                'submit_judge': api_key.allow_submit_judge,
                'register_payments': api_key.allow_register_payments,
                'lookup_licenses': api_key.allow_lookup_licenses,
                'export_licenses': api_key.allow_export_licenses,
                'read_submissions': api_key.allow_read_submissions,
                'sensitive_access': api_key.sensitive_access,
                'write_allowed': api_key.write_allowed,
            },
        })


class SubmissionOptionsView(APIView):
    @extend_schema(responses=SubmissionOptionsSerializer)
    def get(self, request):
        gyms = filter_queryset_for_request(Gym.objects.filter(is_active=True).order_by('name'), request)
        states = filter_queryset_for_request(State.objects.all().order_by('name'), request)
        countries = Country.objects.all().order_by('name')
        return Response({
            'states': [
                {'id': state.pk, 'name': state.name, 'short_name': state.short_name}
                for state in states
            ],
            'gyms': [
                {'id': gym.pk, 'name': gym.name, 'state_id': gym.state_id}
                for gym in gyms
            ],
            'countries': [
                {'id': country.pk, 'name': country.name}
                for country in countries
            ],
            'starter_categories': [
                {'value': value, 'label': label}
                for value, label in SubmissionStarter.SUBMISSION_CATEGORY
            ],
            'payment_statuses': [
                {'value': value, 'label': label}
                for value, label in SubmissionStarter.PAYMENT_STATUS
            ],
        })
