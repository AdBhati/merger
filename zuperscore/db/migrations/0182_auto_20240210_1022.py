# Generated by Django 3.2.20 on 2024-02-10 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0181_alter_appointments_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentassignmentquestion',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentassignmentquestion',
            name='is_visible',
            field=models.BooleanField(default=False),
        ),
    ]
