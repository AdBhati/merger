# Generated by Django 3.2.20 on 2023-12-28 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0140_remove_assignment_sequence'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='pdf_url',
        ),
    ]
