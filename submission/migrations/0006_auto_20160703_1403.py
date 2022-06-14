# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0005_auto_20160302_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gym',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name=b'Email', blank=True),
        ),
        migrations.AlterField(
            model_name='gym',
            name='zip_code',
            field=models.IntegerField(null=True, verbose_name='PLZ', blank=True),
        ),
        migrations.AlterField(
            model_name='submissiongym',
            name='members',
            field=models.IntegerField(
                help_text='Dient nur statistischen Zwecken',
                null=True,
                verbose_name='Anzahl Mitglieder',
                blank=True
            ),
        ),
        migrations.AlterField(
            model_name='submissiongym',
            name='zip_code',
            field=models.IntegerField(verbose_name='PLZ'),
        ),
        migrations.AlterField(
            model_name='submissioninternational',
            name='height',
            field=models.IntegerField(verbose_name='Gr\xf6\xdfe (cm)'),
        ),
        migrations.AlterField(
            model_name='submissioninternational',
            name='zip_code',
            field=models.IntegerField(verbose_name='PLZ'),
        ),
        migrations.AlterField(
            model_name='submissionjudge',
            name='zip_code',
            field=models.IntegerField(verbose_name='PLZ'),
        ),
        migrations.AlterField(
            model_name='submissionstarter',
            name='height',
            field=models.IntegerField(verbose_name='Gr\xf6\xdfe (cm)'),
        ),
        migrations.AlterField(
            model_name='submissionstarter',
            name='zip_code',
            field=models.IntegerField(verbose_name='PLZ'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='type',
            field=models.IntegerField(
                default=-1, choices=[(2, 'Bundesverband'), (3, 'User'), (-1, 'Unbekannt')]
            ),
        ),
    ]
