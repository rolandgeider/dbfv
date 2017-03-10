# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0004_auto_20150408_1731'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='championship',
        ),
        migrations.AddField(
            model_name='championship',
            name='categories',
            field=models.ManyToManyField(to='championship.Category', verbose_name=b'Kategorien'),
            preserve_default=True,
        ),
    ]
