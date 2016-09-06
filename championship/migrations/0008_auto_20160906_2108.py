# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0007_auto_20160727_2318'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points', models.IntegerField(default=0, verbose_name=b'Punkte')),
                ('category', models.ForeignKey(verbose_name=b'Kategorie', to='championship.Category')),
                ('judge', models.ForeignKey(verbose_name=b'Kampfrichter', to='championship.Judge')),
                ('participation', models.ForeignKey(editable=False, to='championship.Participation', verbose_name=b'Teilnahme')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='assessment',
            unique_together=set([('participation', 'category', 'judge')]),
        ),
    ]
