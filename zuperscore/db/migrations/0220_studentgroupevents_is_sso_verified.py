# Generated by Django 3.2.18 on 2024-04-17 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0219_rename_is_answered_timeanalytics_is_answered'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentgroupevents',
            name='is_sso_verified',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
