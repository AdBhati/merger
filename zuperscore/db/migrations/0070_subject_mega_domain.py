# Generated by Django 3.2.20 on 2023-10-03 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0069_auto_20231003_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='mega_domain',
            field=models.BooleanField(default=False),
        ),
    ]
