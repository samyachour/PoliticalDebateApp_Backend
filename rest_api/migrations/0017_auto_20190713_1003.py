# Generated by Django 2.1.7 on 2019-07-13 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0016_auto_20190713_0633'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointimage',
            name='source',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pointimage',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
