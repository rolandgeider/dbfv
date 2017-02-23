# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0007_submissionstarter_terms_and_conditions'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='terms_and_conditions',
            field=models.BooleanField(default=False, verbose_name=b'Hiermit erkl\xc3\xa4re ich mich mit den Regeln des DBFV e.V./IFBB'),
        ),
    ]
