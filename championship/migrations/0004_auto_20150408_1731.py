# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0003_auto_20150407_2217'),
    ]

    operations = [
        migrations.CreateModel(
            name='Placement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('placement', models.IntegerField(default=0, verbose_name=b'Platzierung')),
                ('category', models.ForeignKey(verbose_name=b'Kategorie', to='championship.Category')),
                ('participation', models.ForeignKey(editable=False, to='championship.Participation', verbose_name=b'Teilnahme')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='placement',
            unique_together=set([('participation', 'category')]),
        ),
        migrations.AlterField(
            model_name='participation',
            name='championship',
            field=models.ForeignKey(verbose_name=b'Meisterschaft', to='championship.Championship'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='participation',
            name='participation_nr',
            field=models.IntegerField(verbose_name=b'Teilnehmernummer', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='participation',
            name='submission',
            field=models.ForeignKey(editable=False, to='submission.SubmissionStarter', verbose_name=b'Antrag'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='participation',
            unique_together=set([('championship', 'submission'), ('championship', 'participation_nr')]),
        ),
        migrations.RemoveField(
            model_name='participation',
            name='placement',
        ),
        migrations.RemoveField(
            model_name='participation',
            name='category',
        ),
    ]
