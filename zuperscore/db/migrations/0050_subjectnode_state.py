# Generated by Django 3.2.13 on 2023-05-24 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0049_auto_20230518_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectnode',
            name='state',
            field=models.CharField(choices=[('ACTIVE', 'ACTIVE'), ('ARCHIVED', 'ARCHIVED')], default='ACTIVE', max_length=255),
        ),
    ]
