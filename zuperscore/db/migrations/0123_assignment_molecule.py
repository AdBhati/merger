# Generated by Django 3.2.20 on 2023-12-11 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0122_appointments_host_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='molecule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='molecule', to='db.molecule'),
        ),
    ]
