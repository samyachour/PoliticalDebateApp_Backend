# Generated by Django 2.2.5 on 2019-11-09 23:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0002_delete_pointimage'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='point',
            unique_together={('short_description', 'description')},
        ),
    ]