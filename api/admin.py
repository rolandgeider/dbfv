# Third Party
from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey

# Django
from django.contrib import admin

# dbfv
from api.audit import log_key_revoked
from api.models import APIAccessLog, ScopedAPIKey

# The library registers its own plain APIKey model; keys of that type are never
# accepted by the API, so hide it to avoid a second, non-functional key admin.
admin.site.unregister(APIKey)


@admin.register(ScopedAPIKey)
class ScopedAPIKeyAdmin(APIKeyModelAdmin):
    list_display = [
        *APIKeyModelAdmin.list_display, 'write_allowed', 'sensitive_access',
        'federal_access', 'submission_scope', 'state_scope', 'allowed_ips',
    ]
    list_filter = [
        *APIKeyModelAdmin.list_filter, 'write_allowed', 'sensitive_access',
        'federal_access', 'allow_submit_starter', 'allow_submit_international',
        'allow_submit_gym', 'allow_submit_judge', 'allow_register_payments',
        'allow_lookup_licenses', 'allow_lookup_all_states', 'allow_export_licenses',
        'allow_read_submissions',
    ]
    filter_horizontal = ['allowed_states']

    @admin.display(description='Landesverbände')
    def state_scope(self, obj):
        if obj.federal_access:
            return 'Bund/System'
        names = list(obj.allowed_states.values_list('short_name', flat=True))
        return ', '.join(names) if names else 'Keine'

    @admin.display(description='API-Anträge')
    def submission_scope(self, obj):
        scopes = []
        if obj.allow_submit_starter:
            scopes.append('Starter')
        if obj.allow_submit_international:
            scopes.append('International')
        if obj.allow_submit_gym:
            scopes.append('Studio')
        if obj.allow_submit_judge:
            scopes.append('Kampfrichter')
        if obj.allow_register_payments:
            scopes.append('Zahlung')
        if obj.allow_lookup_licenses:
            scopes.append('Lookup bundesweit' if obj.allow_lookup_all_states else 'Lookup')
        if obj.allow_export_licenses:
            scopes.append('Export')
        if obj.allow_read_submissions:
            scopes.append('Lesen')
        return ', '.join(scopes) if scopes else 'Keine'

    def save_model(self, request, obj, form, change):
        if 'revoked' in form.changed_data and obj.revoked:
            log_key_revoked(obj.prefix, request.user.get_username())
        super().save_model(request, obj, form, change)


@admin.register(APIAccessLog)
class APIAccessLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'key_prefix', 'method', 'path', 'status_code', 'client_ip']
    list_filter = ['status_code', 'method', 'key_prefix', 'created_at']
    search_fields = ['key_prefix', 'client_ip', 'path']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'key_prefix', 'client_ip', 'method', 'path', 'status_code']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
