# Generated by Django 3.2 on 2024-11-18 08:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geospaas_rest_api', '0006_syntoolcomparejob'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkdirCleanupJob',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('geospaas_rest_api.job',),
        ),
    ]
