# Third Party
from rest_framework.permissions import SAFE_METHODS
from rest_framework_api_key.permissions import BaseHasAPIKey

# dbfv
from api.access import api_key_from_request
from api.client_ip import client_ip
from api.models import ScopedAPIKey
from core.models import EmailCron
from submission.models import (
    BankAccount,
    ManagerEmail,
    SubmissionGym,
    SubmissionInternational,
    SubmissionJudge,
    SubmissionStarter,
    UserProfile,
)

# Models carrying personal/financial data — only keys with sensitive_access
# may touch their CRUD endpoints. Stammdaten (Gym/State/Country) stay open.
SENSITIVE_MODELS = {
    BankAccount, UserProfile, ManagerEmail, EmailCron,
    SubmissionStarter, SubmissionInternational, SubmissionGym, SubmissionJudge,
}


class ScopedAPIKeyPermission(BaseHasAPIKey):
    """
    Any valid key may read Stammdaten; writing requires ``write_allowed``,
    sensitive resources require ``sensitive_access``.
    """

    model = ScopedAPIKey

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        api_key = api_key_from_request(request)
        if not api_key:
            return False
        if not api_key.ip_allowed(client_ip(request)):
            return False
        view_model = getattr(getattr(view, 'queryset', None), 'model', None)
        if view_model in {
            SubmissionStarter, SubmissionInternational, SubmissionGym, SubmissionJudge,
        } and request.method in SAFE_METHODS and not api_key.allow_read_submissions:
            return False
        if view_model in SENSITIVE_MODELS and not api_key.sensitive_access:
            return False
        # DELETE on open Stammdaten (Gym/State/Country) cascades into sensitive
        # submissions, so a plain write key must not delete anything.
        if request.method == 'DELETE' and not api_key.sensitive_access:
            return False
        # Views may demand the sensitive scope explicitly (e.g. bulk exports).
        if getattr(view, 'requires_sensitive', False) and not api_key.sensitive_access:
            return False
        if request.method in SAFE_METHODS:
            return True
        # Explicitly marked POST endpoints may perform read-only lookups whose
        # sensitive inputs belong in the request body rather than the URL.
        if request.method == 'POST' and getattr(view, 'read_only_post', False):
            return True
        submission_flag = getattr(view, 'api_submission_permission_flag', None)
        if request.method == 'POST' and submission_flag:
            return bool(getattr(api_key, submission_flag, False))
        return api_key.write_allowed
