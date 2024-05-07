# Generated by Django 3.2.20 on 2023-12-19 04:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0134_auto_20231218_1808'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mothersessionmolecule',
            options={},
        ),
        migrations.AlterField(
            model_name='sessionplan',
            name='mega_domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_plan', to='db.megadomain'),
        ),
        migrations.AlterField(
            model_name='sessionplan',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_plan', to='db.subject'),
        ),
        migrations.AlterModelTable(
            name='mothersessionmolecule',
            table=None,
        ),
    ]
