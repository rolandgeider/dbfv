# Generated by Django 4.0.7 on 2023-03-01 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0014_submissiongym_pdf_sent_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='submissiongym',
            options={'ordering': ['creation_date', 'state']},
        ),
        migrations.AlterModelOptions(
            name='submissionjudge',
            options={'ordering': ['creation_date', 'state']},
        ),
        migrations.RemoveField(
            model_name='submissiongym',
            name='fax_number',
        ),
        migrations.RemoveField(
            model_name='submissiongym',
            name='members',
        ),
        migrations.AddField(
            model_name='submissiongym',
            name='owner',
            field=models.CharField(default='', max_length=30, verbose_name='Inhaber'),
            preserve_default=False,
        ),
    ]
