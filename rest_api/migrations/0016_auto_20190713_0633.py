# Generated by Django 2.1.7 on 2019-07-13 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0015_auto_20190713_0526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='progress',
            name='seen_points',
        ),
        migrations.AddField(
            model_name='progress',
            name='seen_points',
            field=models.ManyToManyField(to='rest_api.Point'),
        ),
    ]
