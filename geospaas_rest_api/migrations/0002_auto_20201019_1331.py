# Generated by Django 3.0 on 2020-10-19 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geospaas_rest_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConvertJob',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('geospaas_rest_api.job',),
        ),
        migrations.CreateModel(
            name='DownloadJob',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('geospaas_rest_api.job',),
        ),
        migrations.AlterField(
            model_name='job',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, help_text='Datetime: creation date of the job', verbose_name='Creation DateTime'),
        ),
        migrations.AlterField(
            model_name='job',
            name='task_id',
            field=models.CharField(help_text='ID of the first task in the job', max_length=255, unique=True),
        ),
    ]