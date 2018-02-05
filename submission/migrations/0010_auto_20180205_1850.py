# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0009_auto_20170223_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionstarter',
            name='house_nr',
            field=models.CharField(default='.', max_length=30, verbose_name='Hausnummer'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='submissioninternational',
            name='category',
            field=models.CharField(max_length=2, verbose_name='Kategorie', choices=[(b'1', 'Jugend-Bikini-Fitness'), (b'2', 'Jugend-Mens Physique'), (b'3', 'Jugend-Bodybuilding'), (b'4', 'Junioren-Bikini-Fitness'), (b'5', 'Junioren-Mens Physique'), (b'6', 'Junioren-Bodybuilding'), (b'7', 'Frauen-Bikini-Fitness'), (b'8', 'Frauen-Fitness-Figur'), (b'9', 'Frauen-Physique'), (b'10', 'Paare'), (b'11', 'Handicappt/Wheelchair'), (b'12', 'Classic Bodybuilding'), (b'13', 'M\xe4nner Physique'), (b'14', 'M\xe4nner Bodybuilding'), (b'15', 'Masters-M\xe4nner BB'), (b'16', 'Masters-M\xe4nner Classic BB'), (b'17', 'Masters-M\xe4nner Physique'), (b'18', 'Masters-Frauen Physique'), (b'19', 'Masters-Frauen Bikini Fitness'), (b'20', 'Masters-Frauen Figur')]),
        ),
        migrations.AlterField(
            model_name='submissionstarter',
            name='category',
            field=models.CharField(max_length=2, verbose_name='Kategorie', choices=[(b'1', 'Bikini-Klasse'), (b'2', 'Frauen Fitness-Figur-Klasse'), (b'3', 'Frauen Bodyklasse'), (b'4', 'Frauen Physiqueklasse'), (b'5', 'Juniorenklasse'), (b'6', 'Classic-Bodybuilding'), (b'7', 'Paare'), (b'8', 'M\xe4nner Physique'), (b'9', 'M\xe4nner Bodyklasse'), (b'10', 'Wellness-Fitness'), (b'11', 'Muscular-Physique'), (b'12', 'Masters-M\xe4nner BB'), (b'13', 'Masters-M\xe4nner Classic BB'), (b'14', 'Masters-M\xe4nner Physique'), (b'15', 'Masters-Frauen Physique'), (b'16', 'Masters-Frauen Bikini Fitness'), (b'17', 'Masters-Frauen Figur')]),
        ),
    ]
