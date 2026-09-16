# Third Party
from rest_framework_api_key.models import AbstractAPIKey

# Django
from django.db import models


class ScopedAPIKey(AbstractAPIKey):
    """
    API key with a configurable write scope.

    A valid, active key may always read (safe HTTP methods). Writing
    (POST/PUT/PATCH/DELETE) additionally requires ``write_allowed``.
    """

    write_allowed = models.BooleanField(
        default=False,
        verbose_name='Schreibzugriff erlaubt',
        help_text='Erlaubt POST/PUT/PATCH/DELETE. Ohne Haken nur Lesezugriff.',
    )
    allowed_ips = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Erlaubte IPs',
        help_text='Kommagetrennte IPs oder CIDR-Bereiche (z. B. "203.0.113.5, '
        '198.51.100.0/24"). Leer = keine IP-Einschränkung.',
    )
    sensitive_access = models.BooleanField(
        default=False,
        verbose_name='Zugriff auf sensible Daten',
        help_text='Erlaubt Zugriff auf personen-/finanzbezogene Ressourcen '
        '(Bankkonten, Benutzerprofile, Rohanträge, interne Modelle). Ohne '
        'Haken nur Stammdaten und Lizenz-Endpoints.',
    )
    federal_access = models.BooleanField(
        default=False,
        verbose_name='Bundes-/Systemzugriff',
        help_text='Erlaubt Zugriff über alle Landesverbände hinweg. Nur für '
        'Bundesverband, interne Dienste oder ausdrücklich geprüfte System-Keys.',
    )
    allow_submit_starter = models.BooleanField(
        default=False,
        verbose_name='Starter-Anträge per API',
        help_text='Erlaubt das Anlegen von Starterlizenz-Anträgen über die Fach-API.',
    )
    allow_submit_international = models.BooleanField(
        default=False,
        verbose_name='Internationale Anträge per API',
        help_text='Erlaubt das Anlegen internationaler Lizenz-Anträge über die Fach-API.',
    )
    allow_submit_gym = models.BooleanField(
        default=False,
        verbose_name='Studio-Anträge per API',
        help_text='Erlaubt das Anlegen von Studio-/Vereinslizenz-Anträgen über die Fach-API.',
    )
    allow_submit_judge = models.BooleanField(
        default=False,
        verbose_name='Kampfrichter-Anträge per API',
        help_text='Erlaubt das Anlegen von Kampfrichterlizenz-Anträgen über die Fach-API.',
    )
    allow_register_payments = models.BooleanField(
        default=False,
        verbose_name='Zahlungen per API registrieren',
        help_text='Erlaubt Zahlungsdaten beim Anlegen eines API-Antrags zu speichern.',
    )
    allow_lookup_licenses = models.BooleanField(
        default=False,
        verbose_name='Lizenz-Lookup per API',
        help_text='Erlaubt gezielte, datensparsame Lizenz-Gültigkeitsabfragen.',
    )
    allow_export_licenses = models.BooleanField(
        default=False,
        verbose_name='Lizenz-Export per API',
        help_text='Erlaubt den Massen-Export gültiger Lizenzen.',
    )
    allow_read_submissions = models.BooleanField(
        default=False,
        verbose_name='Anträge per API lesen',
        help_text='Erlaubt Roh-Antragsdaten über die generischen Submission-Endpunkte zu lesen.',
    )
    allowed_states = models.ManyToManyField(
        'submission.State',
        blank=True,
        related_name='api_keys',
        verbose_name='Erlaubte Landesverbände',
        help_text='Beschränkt diesen Key auf die ausgewählten Landesverbände. '
        'Für normale Landesverbands-Keys muss mindestens ein Verband gesetzt sein.',
    )

    def ip_allowed(self, client_ip):
        """True if client_ip matches the allowlist (empty allowlist = allow all)."""
        # Standard Library
        import ipaddress

        if not self.allowed_ips.strip():
            return True
        try:
            addr = ipaddress.ip_address(client_ip)
        except ValueError:
            return False
        for entry in self.allowed_ips.split(','):
            entry = entry.strip()
            if not entry:
                continue
            try:
                if addr in ipaddress.ip_network(entry, strict=False):
                    return True
            except ValueError:
                continue
        return False

    def has_state_scope(self):
        """True if this key is restricted to one or more state associations."""
        if not self.pk:
            return False
        return self.allowed_states.exists()

    def allowed_state_ids(self):
        """Return state IDs this key may access."""
        if not self.pk:
            return []
        return list(self.allowed_states.values_list('pk', flat=True))

    def has_federal_access(self):
        """True if this key may access data across all state associations."""
        return bool(self.federal_access)

    class Meta(AbstractAPIKey.Meta):
        verbose_name = 'API-Key'
        verbose_name_plural = 'API-Keys'


class APIAccessLog(models.Model):
    """Datensparsamer API-Zugriffsverlauf fuer Admin-Kontrolle."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    key_prefix = models.CharField(max_length=8, blank=True, default='-', db_index=True)
    client_ip = models.GenericIPAddressField(blank=True, null=True, db_index=True)
    method = models.CharField(max_length=8, db_index=True)
    path = models.CharField(max_length=255, db_index=True)
    status_code = models.PositiveSmallIntegerField(db_index=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'API-Zugriff'
        verbose_name_plural = 'API-Zugriffe'
