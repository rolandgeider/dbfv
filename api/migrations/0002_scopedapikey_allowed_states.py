from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        ('submission', '0015_alter_submissiongym_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='scopedapikey',
            name='allowed_states',
            field=models.ManyToManyField(
                blank=True,
                help_text='Beschränkt diesen Key auf die ausgewählten Landesverbände. Leer = Bundes-/System-Key ohne Landesverbandsgrenze.',
                related_name='api_keys',
                to='submission.state',
                verbose_name='Erlaubte Landesverbände',
            ),
        ),
    ]
