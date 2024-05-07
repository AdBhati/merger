# Generated by Django 3.2.20 on 2023-10-06 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0084_delete_agenda'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('mega_domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_plan', to='db.megadomain')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_plan', to='db.subject')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
