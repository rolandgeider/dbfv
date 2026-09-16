"""Shared API-key access helpers for state-scoped data isolation."""

# dbfv
from api.models import ScopedAPIKey
from submission.models import (
    BankAccount,
    Gym,
    State,
    SubmissionGym,
    SubmissionInternational,
    SubmissionJudge,
    SubmissionStarter,
    UserProfile,
)


def api_key_from_request(request):
    """Return the validated ScopedAPIKey for this request, or None."""
    cached = getattr(request, '_scoped_api_key', None)
    if cached is not None:
        return cached

    key = request.META.get('HTTP_AUTHORIZATION', '')
    if key.startswith('Api-Key '):
        key = key.removeprefix('Api-Key ').strip()
    else:
        key = request.META.get('HTTP_X_API_KEY', '').strip()

    if not key:
        return None
    try:
        api_key = ScopedAPIKey.objects.get_from_key(key)
    except ScopedAPIKey.DoesNotExist:
        return None
    request._scoped_api_key = api_key
    return api_key


def allowed_state_ids_for_request(request):
    """Return scoped state IDs, None for federal access, [] for no state access."""
    api_key = api_key_from_request(request)
    if not api_key:
        return []
    if api_key.has_federal_access():
        return None
    return api_key.allowed_state_ids()


def filter_queryset_for_request(queryset, request):
    """
    Apply the API key's Landesverband scope to known models.

    ``federal_access`` is intentionally unrestricted for federal or internal
    integration keys. Keys without federal_access and without allowed_states see
    no state-bound rows.
    """
    state_ids = allowed_state_ids_for_request(request)
    if state_ids is None:
        return queryset

    model = queryset.model
    if model is State:
        return queryset.filter(pk__in=state_ids)
    if model is Gym:
        return queryset.filter(state_id__in=state_ids)
    if model in (SubmissionStarter, SubmissionInternational):
        return queryset.filter(gym__state_id__in=state_ids)
    if model in (SubmissionGym, SubmissionJudge, UserProfile):
        return queryset.filter(state_id__in=state_ids)
    if model is BankAccount:
        return queryset.filter(state__id__in=state_ids).distinct()
    return queryset


def state_ids_for_object_data(model, attrs):
    """Extract target state IDs touched by a create/update serializer payload."""
    if model is Gym and attrs.get('state'):
        return [attrs['state'].pk]
    if model in (SubmissionGym, SubmissionJudge, UserProfile) and attrs.get('state'):
        return [attrs['state'].pk]
    if model in (SubmissionStarter, SubmissionInternational) and attrs.get('gym'):
        return [attrs['gym'].state_id]
    return []
