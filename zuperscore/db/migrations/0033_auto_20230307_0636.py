# Generated by Django 3.2.13 on 2023-03-07 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0032_userattempt_stat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_answered',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_correct',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_incorrect',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_questions',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_unanswered',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_unattempted',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_unvisited',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userassessmentsession',
            name='total_visited',
            field=models.IntegerField(default=0),
        ),
    ]
