from django.db import migrations, models


def mark_existing_keys_as_federal(apps, schema_editor):
    ScopedAPIKey = apps.get_model('api', 'ScopedAPIKey')
    ScopedAPIKey.objects.update(federal_access=True)


def unmark_existing_keys_as_federal(apps, schema_editor):
    ScopedAPIKey = apps.get_model('api', 'ScopedAPIKey')
    ScopedAPIKey.objects.update(federal_access=False)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_scopedapikey_allowed_states'),
    ]

    operations = [
        migrations.AddField(
            model_name='scopedapikey',
            name='federal_access',
            field=models.BooleanField(
                default=False,
                help_text='Erlaubt Zugriff über alle Landesverbände hinweg. Nur für Bundesverband, interne Dienste oder ausdrücklich geprüfte System-Keys.',
                verbose_name='Bundes-/Systemzugriff',
            ),
        ),
        migrations.RunPython(
            mark_existing_keys_as_federal,
            reverse_code=unmark_existing_keys_as_federal,
        ),
    ]
