# Generated by Django 3.2.13 on 2023-02-01 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0022_auto_20230201_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userassessmentsession',
            name='state',
            field=models.CharField(choices=[('UNTOUCHED', 'UNTOUCHED'), ('STARTED', 'STARTED'), ('IN_PROGRESS', 'IN_PROGRESS'), ('COMPLETED', 'COMPLETED'), ('CANCELLED', 'CANCELLED'), ('ARCHIVED', 'ARCHIVED'), ('ANALYSED', 'ANALYSED')], default='UNTOUCHED', max_length=255),
        ),
    ]
