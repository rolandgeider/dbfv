"""Audit logging for API usage.

Never logs the API-key secret, the request body, or the query string (which can
carry search data). Only the key prefix, client IP, method, path and status.
"""
# Standard Library
import logging

# dbfv
from api.models import APIAccessLog

logger = logging.getLogger('dbfv.audit')


def key_prefix(request):
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if auth.startswith('Api-Key '):
        token = auth[len('Api-Key '):].strip()
        # Prefix only, never the secret; bounded so attacker-controlled input
        # cannot bloat the log or overflow APIAccessLog.key_prefix.
        return token.split('.', 1)[0][:8] or '-'
    return '-'


def log_api_access(request, status_code, client):
    prefix = key_prefix(request)
    level = logging.WARNING if status_code in (401, 403, 429) else logging.INFO
    logger.log(
        level,
        'api access key=%s ip=%s method=%s path=%s status=%s',
        prefix, client or '-', request.method, request.path, status_code,
    )
    try:
        APIAccessLog.objects.create(
            key_prefix=prefix,
            client_ip=client or None,
            method=request.method[:8],
            path=request.path[:255],
            status_code=status_code,
        )
    except Exception:
        logger.exception('api access db audit failed')


def log_key_revoked(prefix, actor):
    logger.warning('api key revoked key=%s by=%s', prefix or '-', actor or '-')
