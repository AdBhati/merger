# Generated by Django 3.2.20 on 2023-10-06 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0085_sessionplan'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sessionplan',
            options={'verbose_name': 'SessionPlan', 'verbose_name_plural': 'SessionPlans'},
        ),
        migrations.AlterModelTable(
            name='sessionplan',
            table='session_plan',
        ),
    ]
