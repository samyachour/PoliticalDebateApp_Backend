# Generated by Django 2.1.7 on 2019-03-03 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0003_auto_20190303_0913'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_password', models.CharField(max_length=255)),
                ('new_password', models.CharField(max_length=255)),
            ],
        ),
    ]
