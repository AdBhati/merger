# Generated by Django 3.2.20 on 2024-02-07 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0176_auto_20240203_1750'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointmentmolecule',
            name='session_plan',
        ),
        migrations.AddField(
            model_name='appointmentmolecule',
            name='appointment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment', to='db.appointments'),
        ),
        migrations.AddField(
            model_name='appointmentmolecule',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
