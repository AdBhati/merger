# Generated by Django 3.2.13 on 2023-04-18 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0037_alter_userattempt_stat'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='set_password',
            field=models.BooleanField(default=False),
        ),
    ]
