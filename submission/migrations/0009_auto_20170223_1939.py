# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0008_userprofile_terms_and_conditions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionstarter',
            name='category',
            field=models.CharField(max_length=2, verbose_name='Kategorie', choices=[(b'1', 'Bikini-Klasse'), (b'2', 'Frauen Fitness-Figur-Klasse'), (b'3', 'Frauen Bodyklasse'), (b'4', 'Frauen Physiqueklasse'), (b'5', 'Juniorenklasse'), (b'6', 'Classic-Bodybuilding'), (b'7', 'Paare'), (b'8', 'M\xe4nner Physique'), (b'9', 'M\xe4nner Bodyklasse'), (b'10', 'Wellness-Fitness'), (b'11', 'Muscular-Physique')]),
        ),
    ]
