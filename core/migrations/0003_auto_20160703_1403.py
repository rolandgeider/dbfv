# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_emailcron_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcron',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
