# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('championship', models.ForeignKey(verbose_name=b'Meistershaft', to='championship.Championship')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='championship',
            name='state',
            field=models.ForeignKey(verbose_name=b'Bundesland', to='submission.State'),
            preserve_default=True,
        ),
    ]
