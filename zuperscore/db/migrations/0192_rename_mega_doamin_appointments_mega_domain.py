# Generated by Django 3.2.20 on 2024-03-07 07:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0191_appointments_mega_doamin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointments',
            old_name='mega_doamin',
            new_name='mega_domain',
        ),
    ]
