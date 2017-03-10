# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0009_auto_20160911_1314'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='assessment',
            unique_together=set([]),
        ),
    ]
