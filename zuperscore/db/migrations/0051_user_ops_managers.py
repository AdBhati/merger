# Generated by Django 3.2.13 on 2023-05-25 08:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0050_subjectnode_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ops_managers',
            field=models.ManyToManyField(blank=True, related_name='_db_user_ops_managers_+', to=settings.AUTH_USER_MODEL),
        ),
    ]
