# Generated by Django 3.2.13 on 2022-11-22 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0011_questionnode_sequence'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questionnode',
            options={'ordering': ('sequence', 'created_at')},
        ),
    ]
