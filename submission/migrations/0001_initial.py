# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('owner_name', models.CharField(max_length=100, verbose_name=b'Beg\xc3\xbcnstigter')),
                ('iban', models.CharField(max_length=34, verbose_name=b'IBAN')),
                ('bic', models.CharField(help_text='Nur bei Auslands\xfcberweisung n\xf6tig', max_length=11, verbose_name=b'BIC')),
                ('bank_name', models.CharField(max_length=30, verbose_name=b'Bankname')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gym',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Name')),
                ('email', models.EmailField(max_length=75, null=True, verbose_name=b'Email', blank=True)),
                ('owner', models.CharField(max_length=100, null=True, verbose_name=b'Inhaber', blank=True)),
                ('zip_code', models.IntegerField(max_length=5, null=True, verbose_name='PLZ', blank=True)),
                ('city', models.CharField(max_length=30, null=True, verbose_name='Ort', blank=True)),
                ('street', models.CharField(max_length=30, null=True, verbose_name='Stra\xdfe', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Ist aktiv')),
            ],
            options={
                'ordering': ['state__name', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManagerEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=30, verbose_name='Email')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Name')),
                ('short_name', models.CharField(max_length=3, verbose_name=b'K\xc3\xbcrzel')),
                ('email', models.EmailField(max_length=120, verbose_name=b'Email', blank=True)),
                ('bank_account', models.ForeignKey(verbose_name=b'Bankkonto', to='submission.BankAccount', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmissionGym',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Creation date')),
                ('submission_status', models.CharField(default=b'1', max_length=2, choices=[(b'1', b'Eingegangen'), (b'2', b'Bewilligt'), (b'3', b'Abgelehnt')])),
                ('mail_merge', models.BooleanField(default=False, editable=False)),
                ('name', models.CharField(help_text='Name des Studios oder Verein', max_length=30, verbose_name='Name')),
                ('founded', models.DateField(verbose_name='Gegr\xfcndet am')),
                ('street', models.CharField(max_length=30, verbose_name='Stra\xdfe')),
                ('zip_code', models.IntegerField(max_length=5, verbose_name='PLZ')),
                ('city', models.CharField(max_length=30, verbose_name='Ort')),
                ('tel_number', models.CharField(max_length=20, verbose_name='Tel. Nr.')),
                ('fax_number', models.CharField(max_length=20, verbose_name='Fax. Nr.')),
                ('email', models.EmailField(max_length=120, verbose_name='Email')),
                ('members', models.IntegerField(help_text='Dient nur statistischen Zwecken', max_length=5, null=True, verbose_name='Anzahl Mitglieder', blank=True)),
                ('gym', models.OneToOneField(null=True, editable=False, to='submission.Gym', blank=True, verbose_name=b'Studio', on_delete=models.CASCADE)),
                ('state', models.ForeignKey(verbose_name='Landesverband', to='submission.State',  on_delete=models.CASCADE)),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmissionJudge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Creation date')),
                ('submission_status', models.CharField(default=b'1', max_length=2, choices=[(b'1', b'Eingegangen'), (b'2', b'Bewilligt'), (b'3', b'Abgelehnt')])),
                ('mail_merge', models.BooleanField(default=False, editable=False)),
                ('last_name', models.CharField(max_length=30, verbose_name=b'Familienname')),
                ('first_name', models.CharField(max_length=30, verbose_name=b'Vorname')),
                ('street', models.CharField(max_length=30, verbose_name='Stra\xdfe')),
                ('zip_code', models.IntegerField(max_length=5, verbose_name='PLZ')),
                ('city', models.CharField(max_length=30, verbose_name='Ort')),
                ('tel_number', models.CharField(max_length=20, verbose_name='Tel. Nr.')),
                ('email', models.EmailField(max_length=120, null=True, verbose_name='Email', blank=True)),
                ('state', models.ForeignKey(verbose_name='Landesverband', to='submission.State', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmissionStarter',
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
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(default=-1, max_length=1, choices=[(2, 'Bundesverband'), (3, 'User'), (-1, 'Unbekannt')])),
                ('state', models.ForeignKey(blank=True, to='submission.State', null=True, on_delete=models.CASCADE)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL,  on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gym',
            name='state',
            field=models.ForeignKey(verbose_name=b'Bundesland', to='submission.State', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
