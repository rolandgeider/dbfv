# Third Party
from rest_framework import serializers, viewsets
from rest_framework.exceptions import PermissionDenied

# dbfv
from api.access import (
    FEDERAL_ONLY_MODELS,
    FEDERAL_WRITE_ONLY_MODELS,
    allowed_state_ids_for_request,
    filter_queryset_for_request,
    state_ids_for_object_data,
)
from core.models import EmailCron
from submission.models import (
    BankAccount,
    Country,
    Gym,
    ManagerEmail,
    State,
    SubmissionGym,
    SubmissionInternational,
    SubmissionJudge,
    SubmissionStarter,
    UserProfile,
)

# All models exposed via CRUD. Access per key is configurable: read for any
# valid key, write only when the key has write_allowed set.
API_MODELS = [
    Gym,
    State,
    Country,
    BankAccount,
    ManagerEmail,
    EmailCron,
    UserProfile,
    SubmissionStarter,
    SubmissionInternational,
    SubmissionGym,
    SubmissionJudge,
]

# Submissions are read-only via the API: their `user` field is editable=False
# and gets no request user under API-key auth (create → IntegrityError), and
# status changes must run through the domain workflow (e.g. Gym activation on
# approval), which a generic serializer.save() would bypass.
READ_ONLY_MODELS = {
    SubmissionStarter, SubmissionInternational, SubmissionGym, SubmissionJudge,
}


# Field types django-filter can filter on with an exact lookup.
_FILTERABLE = {
    'CharField', 'TextField', 'EmailField', 'SlugField', 'BooleanField',
    'IntegerField', 'BigIntegerField', 'SmallIntegerField', 'PositiveIntegerField',
    'PositiveSmallIntegerField', 'DateField', 'DateTimeField', 'ForeignKey',
}
_SEARCHABLE = {'CharField', 'TextField', 'EmailField', 'SlugField'}


def _serializer_for(model):
    meta = type('Meta', (), {'model': model, 'fields': '__all__'})
    return type(f'{model.__name__}Serializer', (serializers.ModelSerializer,), {'Meta': meta})


def _viewset_for(model):
    fields = model._meta.fields  # concrete local fields (FKs by name, no m2m/reverse)
    base = viewsets.ReadOnlyModelViewSet if model in READ_ONLY_MODELS else viewsets.ModelViewSet
    serializer_cls = _serializer_for(model)

    class StateScopedViewSet(base):
        queryset = model._default_manager.all().order_by('pk')
        serializer_class = serializer_cls
        # ?field=value exact filter, ?search=, ?ordering=
        filterset_fields = [f.name for f in fields if f.get_internal_type() in _FILTERABLE]
        search_fields = [f.name for f in fields if f.get_internal_type() in _SEARCHABLE]
        ordering_fields = '__all__'

        def get_queryset(self):
            return filter_queryset_for_request(super().get_queryset(), self.request)

        def _enforce_write_scope(self, serializer):
            state_ids = allowed_state_ids_for_request(self.request)
            if state_ids is None:
                return
            if model in FEDERAL_ONLY_MODELS or model in FEDERAL_WRITE_ONLY_MODELS:
                raise PermissionDenied(
                    'Diese Ressource ist nur mit Bundes-/Systemzugriff bearbeitbar.'
                )
            if model is State and self.action in {'create', 'update', 'partial_update'}:
                raise PermissionDenied('Dieser API-Key darf keine Landesverbände bearbeiten.')
            target_state_ids = state_ids_for_object_data(model, serializer.validated_data)
            if not state_ids and target_state_ids:
                raise PermissionDenied(
                    'Dieser API-Key ist keinem Landesverband zugeordnet.'
                )
            if any(state_id not in state_ids for state_id in target_state_ids):
                raise PermissionDenied(
                    'Dieser API-Key darf keine Daten anderer Landesverbände bearbeiten.'
                )

        def perform_create(self, serializer):
            self._enforce_write_scope(serializer)
            serializer.save()

        def perform_update(self, serializer):
            self._enforce_write_scope(serializer)
            serializer.save()

        def perform_destroy(self, instance):
            # Deleting a State cascades into every gym, profile and submission
            # of that Landesverband; only federal/system keys may do that.
            scoped = allowed_state_ids_for_request(self.request) is not None
            if scoped and model is State:
                raise PermissionDenied('Dieser API-Key darf keine Landesverbände löschen.')
            if scoped and model in FEDERAL_WRITE_ONLY_MODELS:
                raise PermissionDenied(
                    'Diese Ressource ist nur mit Bundes-/Systemzugriff löschbar.'
                )
            instance.delete()

    StateScopedViewSet.__name__ = f'{model.__name__}ViewSet'
    return type(
        f'{model.__name__}ViewSet',
        (StateScopedViewSet,),
        {
        },
    )


# {url slug: viewset} — consumed by api/urls.py router.
VIEWSETS = {model.__name__.lower(): _viewset_for(model) for model in API_MODELS}
