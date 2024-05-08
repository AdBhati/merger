# Generated by Django 3.2.20 on 2024-02-15 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0069_alter_school_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assessment',
            name='is_extended',
        ),
        migrations.RemoveField(
            model_name='assessment',
            name='is_tutor_test',
        ),
        migrations.AddField(
            model_name='assessment',
            name='assessment_type',
            field=models.CharField(choices=[('STUDENT', 'STUDENT'), ('TUTOR', 'TUTOR'), ('EXTENDED', 'EXTENDED')], default='STUDENT', max_length=255),
        ),
    ]
