# Generated by Django 3.2.13 on 2023-03-24 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0035_alter_userattempt_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referred_by',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='test_results',
            field=models.JSONField(null=True),
        ),
    ]
