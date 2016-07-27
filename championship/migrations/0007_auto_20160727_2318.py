# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0006_judge'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='placement',
            unique_together=set([('participation', 'category', 'placement')]),
        ),
    ]
