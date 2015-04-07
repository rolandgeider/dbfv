# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0001_initial'),
        ('championship', '0002_auto_20150321_2108'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('participation_nr', models.IntegerField(editable=False)),
                ('placement', models.IntegerField(default=0)),
                ('category', models.ForeignKey(to='championship.Category')),
                ('championship', models.ForeignKey(to='championship.Championship')),
                ('submission', models.ForeignKey(editable=False, to='submission.SubmissionStarter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='participation',
            unique_together=set([('championship', 'category', 'submission'), ('championship', 'participation_nr'), ('championship', 'category', 'placement')]),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='championship',
            options={'ordering': ['-date', 'name']},
        ),
        migrations.AlterField(
            model_name='category',
            name='championship',
            field=models.ForeignKey(editable=False, to='championship.Championship', verbose_name=b'Meistershaft'),
            preserve_default=True,
        ),
    ]
