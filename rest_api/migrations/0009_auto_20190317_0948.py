# Generated by Django 2.1.7 on 2019-03-17 09:48

import datetime
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import rest_api.models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0008_progress_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='debate',
            name='subtitle',
        ),
        migrations.AddField(
            model_name='debate',
            name='debate_map',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=rest_api.models.get_default_data_dict),
        ),
        migrations.AddField(
            model_name='debate',
            name='last_updated',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]