# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0006_auto_20160703_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionstarter',
            name='terms_and_conditions',
            field=models.BooleanField(
                default=False,
                verbose_name=b'Hiermit erkl\xc3\xa4re ich mich mit den Regeln des DBFV e.V./IFBB'
            ),
            preserve_default=False,
        ),
    ]
