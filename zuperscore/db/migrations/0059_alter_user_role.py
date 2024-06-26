# Generated by Django 3.2.13 on 2023-08-17 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0058_user_profile_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('user', 'User'), ('tutor', 'Tutor'), ('typist', 'Typist'), ('manager', 'Manager'), ('prep_manager', 'Prep Manager'), ('sso_manager', 'SSO Manager')], default='user', max_length=64),
        ),
    ]
