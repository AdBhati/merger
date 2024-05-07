# Generated by Django 3.2.20 on 2024-02-08 05:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0177_auto_20240207_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedBack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('comment', models.CharField(max_length=500)),
                ('ratings', models.CharField(max_length=255)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stundet_comment', to=settings.AUTH_USER_MODEL)),
                ('tutor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tutor_comment', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'feedbacks',
            },
        ),
    ]
