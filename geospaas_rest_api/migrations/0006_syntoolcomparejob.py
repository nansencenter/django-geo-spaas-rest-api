# Generated by Django 3.2 on 2024-11-14 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geospaas_rest_api', '0005_alter_job_task_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyntoolCompareJob',
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
