# Generated by Django 3.2.20 on 2023-12-07 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0117_auto_20231207_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='molecule',
            name='molecule_topic_subtopic_id',
        ),
    ]
