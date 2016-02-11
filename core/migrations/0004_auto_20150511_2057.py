# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_emaillog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailcron',
            name='body',
        ),
        migrations.RemoveField(
            model_name='emailcron',
            name='subject',
        ),
        migrations.AddField(
            model_name='emailcron',
            name='log',
            field=models.ForeignKey(default=1, editable=False, to='core.EmailLog'),
            preserve_default=False,
        ),
    ]
