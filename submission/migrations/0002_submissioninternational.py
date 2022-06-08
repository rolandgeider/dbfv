# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('submission', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionInternational',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Creation date')),
                ('submission_status', models.CharField(default=b'1', max_length=2, choices=[(b'1', b'Eingegangen'), (b'2', b'Bewilligt'), (b'3', b'Abgelehnt')])),
                ('mail_merge', models.BooleanField(default=False, editable=False)),
                ('date_of_birth', models.DateField(verbose_name='Geburtsdatum')),
                ('active_since', models.CharField(max_length=20, verbose_name='Aktiv seit')),
                ('last_name', models.CharField(max_length=30, verbose_name='Familienname')),
                ('first_name', models.CharField(max_length=30, verbose_name='Vorname')),
                ('street', models.CharField(max_length=30, verbose_name='Stra\xdfe')),
                ('zip_code', models.IntegerField(max_length=5, verbose_name='PLZ')),
                ('city', models.CharField(max_length=30, verbose_name='Ort')),
                ('tel_number', models.CharField(max_length=20, verbose_name='Tel. Nr.')),
                ('email', models.EmailField(max_length=120, verbose_name='Email')),
                ('height', models.IntegerField(max_length=3, verbose_name='Gr\xf6\xdfe (cm)')),
                ('weight', models.DecimalField(verbose_name='Wettkampfgewicht (kg)', max_digits=5, decimal_places=2)),
                ('category', models.CharField(max_length=1, verbose_name='Kategorie', choices=[(b'1', 'Bikini-Klasse'), (b'2', 'Frauen Fitness-Figur-Klasse'), (b'3', 'Frauen Bodyklasse'), (b'4', 'Frauen Physiqueklasse'), (b'5', 'Juniorenklasse'), (b'6', 'Classic-Bodybuilding'), (b'7', 'Paare'), (b'8', 'M\xe4nner Physique'), (b'9', 'M\xe4nner Bodyklasse')])),
                ('championship', models.CharField(max_length=150, verbose_name='Meisterschaft')),
                ('championship_date', models.DateField(verbose_name='Datum der Meisterschaft')),
                ('submission_last_year', models.BooleanField(default=False, verbose_name='Im Vorjahr wurde bereits eine Lizenz beantragt')),
                ('gym', models.ForeignKey(verbose_name=b'Studio', to='submission.Gym', on_delete=models.CASCADE)),
                ('nationality', models.ForeignKey(default=37, verbose_name='Staatsangeh\xf6rigkeit', to='submission.Country', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['creation_date', 'gym'],
            },
            bases=(models.Model,),
        ),
    ]
