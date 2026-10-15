# external_reference: '' -> NULL for web submissions, then unique per API key
# together with api_key_prefix. NULL never collides (SQLite, PostgreSQL,
# MySQL alike), so the constraint needs no backend-specific condition.

from django.db import migrations, models

MODELS = ('submissionstarter', 'submissioninternational', 'submissiongym', 'submissionjudge')


def blank_to_null(apps, schema_editor):
    for name in MODELS:
        model = apps.get_model('submission', name)
        model.objects.filter(external_reference='').update(external_reference=None)


def null_to_blank(apps, schema_editor):
    for name in MODELS:
        model = apps.get_model('submission', name)
        model.objects.filter(external_reference__isnull=True).update(external_reference='')


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0017_submissiongym_external_reference_and_more'),
    ]

    operations = [
        *[
            migrations.AlterField(
                model_name=name,
                name='external_reference',
                field=models.CharField(
                    blank=True, default=None, editable=False, max_length=120, null=True
                ),
            )
            for name in MODELS
        ],
        migrations.RunPython(blank_to_null, null_to_blank),
        *[
            migrations.AddConstraint(
                model_name=name,
                constraint=models.UniqueConstraint(
                    fields=('api_key_prefix', 'external_reference'),
                    name=f'{name}_api_reference_unique',
                ),
            )
            for name in MODELS
        ],
    ]
