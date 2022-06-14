# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='EmailCron',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True, primary_key=True
                    )
                ),
                ('subject', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=75)),
            ],
            options={},
            bases=(models.Model, ),
        ),
    ]
