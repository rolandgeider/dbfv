# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0010_auto_20161005_2235'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_type',
            field=models.CharField(default=b'3', max_length=6, choices=[(b'3', b'Bodybuilding allgemein (3 Runden)'), (b'3', b'Andere Klassen mit nur 2 Runden')]),
        ),
    ]
