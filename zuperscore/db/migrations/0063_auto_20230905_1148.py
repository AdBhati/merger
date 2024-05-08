# Generated by Django 3.2.13 on 2023-09-05 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0062_auto_20230825_1523'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domain',
            name='subject',
        ),
        migrations.CreateModel(
            name='MegaDomain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mega_domains', to='db.subject')),
            ],
            options={
                'verbose_name': 'MegaDomain',
                'verbose_name_plural': 'MegaDomains',
                'db_table': 'mega_domains',
            },
        ),
    ]
