# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0002_submissioninternational'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissioninternational',
            name='active_since',
        ),
        migrations.RemoveField(
            model_name='submissioninternational',
            name='submission_last_year',
        ),
        migrations.AlterField(
            model_name='submissioninternational',
            name='category',
            field=models.CharField(max_length=1, verbose_name='Kategorie', choices=[(b'1', 'Bikini-Klasse'), (b'2', 'Junior-Klasse'), (b'3', 'Junior-Bodybuilding'), (b'4', 'Junior Physique'), (b'5', 'Jugend-Klasse'), (b'6', 'Jugend-Bodybuilding'), (b'7', 'Jugend Physique'), (b'8', 'Frauen Fitness-Figur-Klasse'), (b'9', 'Frauen Bodyklasse'), (b'10', 'Frauen Physiqueklasse'), (b'11', 'Classic-Bodybuilding'), (b'12', 'Paare'), (b'13', 'M\xe4nner Physique'), (b'14', 'M\xe4nner Bodyklasse')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='submissioninternational',
            name='weight',
            field=models.DecimalField(verbose_name='Wettkampfgewicht in kg (ca.)', max_digits=5, decimal_places=2),
            preserve_default=True,
        ),
    ]
