# Generated by Django 3.2.13 on 2023-06-14 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0053_auto_20230605_2109'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assessment',
            old_name='sigma',
            new_name='english_sigma',
        ),
        migrations.RenameField(
            model_name='assessment',
            old_name='xbar',
            new_name='english_xbar',
        ),
        migrations.AddField(
            model_name='assessment',
            name='math_sigma',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='math_xbar',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
