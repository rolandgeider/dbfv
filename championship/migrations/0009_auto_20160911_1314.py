# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0008_auto_20160910_2046'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assessment',
            options={'ordering': ('participation', 'judge', 'points')},
        ),
        migrations.AlterModelOptions(
            name='placement',
            options={'ordering': ('category', 'placement')},
        ),
        migrations.AddField(
            model_name='placement',
            name='points',
            field=models.PositiveSmallIntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='judge',
            field=models.ForeignKey(editable=False, to='championship.Judge', verbose_name=b'Kampfrichter'),
        ),
        migrations.AlterField(
            model_name='assessmentcollection',
            name='round',
            field=models.PositiveSmallIntegerField(verbose_name=b'Runde'),
        ),
        migrations.AlterUniqueTogether(
            name='placement',
            unique_together=set([('participation', 'category')]),
        ),
    ]
