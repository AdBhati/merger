# Generated by Django 3.2.20 on 2023-12-19 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0135_auto_20231219_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='mothersessionmolecule',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mothersessionmolecule',
            name='name',
            field=models.CharField(default='Session Plan', max_length=255),
        ),
    ]
