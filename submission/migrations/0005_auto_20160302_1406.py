# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0004_submissioninternational_best_placement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissioninternational',
            name='best_placement',
            field=models.CharField(help_text=b'Beste Platzierung auf einer deutschen DBFV/IFBB-Meisterschaft, mit Datum und Kategorie', max_length=150, verbose_name='Beste Platzierung'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='submissioninternational',
            name='category',
            field=models.CharField(max_length=2, verbose_name='Kategorie', choices=[(b'1', 'Jugend-Bikini-Fitness'), (b'2', 'Jugend-Mens Physique'), (b'3', 'Jugend-Bodybuilding'), (b'4', 'Junioren-Bikini-Fitness'), (b'5', 'Junioren-Mens Physique'), (b'6', 'Junioren-Bodybuilding'), (b'7', 'Frauen-Bikini-Fitness'), (b'8', 'Frauen-Fitness-Figur'), (b'9', 'Frauen-Physique'), (b'10', 'Paare'), (b'11', 'Handicappt/Wheelchair'), (b'12', 'Classic Bodybuilding'), (b'13', 'M\xe4nner Physique'), (b'14', 'M\xe4nner Bodybuilding')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='submissioninternational',
            name='championship',
            field=models.CharField(help_text='Meisterschaft in der Du starten m\xf6chtest', max_length=150, verbose_name='Meisterschaft'),
            preserve_default=True,
        ),
    ]
