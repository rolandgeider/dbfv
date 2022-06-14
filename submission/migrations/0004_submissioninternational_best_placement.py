# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0003_auto_20160222_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissioninternational',
            name='best_placement',
            field=models.CharField(
                default='',
                max_length=150,
                verbose_name=
                'Beste Platzierung auf einer deutschen DBFV/IFBB-Meisterschaft, Datum und Kategorie'
            ),
            preserve_default=False,
        ),
    ]
