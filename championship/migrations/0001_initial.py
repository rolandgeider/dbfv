# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Championship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('date', models.DateField(verbose_name=b'Datum')),
                ('state', models.ForeignKey(to='submission.State')),
            ],
            options={
                'ordering': ['date', 'name'],
            },
            bases=(models.Model,),
        ),
    ]
