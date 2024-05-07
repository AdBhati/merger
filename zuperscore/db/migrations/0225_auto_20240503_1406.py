# Generated by Django 3.2.18 on 2024-05-03 08:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0224_megadomain_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassClassification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('type', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'class_classification',
            },
        ),
        migrations.AddField(
            model_name='studentcpeareport',
            name='is_student_view',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='tutor_slot',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='TutorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('slot', models.IntegerField(default=0)),
                ('total_week_supply', models.IntegerField(default=0)),
                ('total_weekly_load', models.IntegerField(default=0)),
                ('remaining_weekly_supply', models.IntegerField(default=0)),
                ('total_monthly_load', models.IntegerField(default=0)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_availability', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tutor_availablity',
            },
        ),
        migrations.CreateModel(
            name='StudentJourney',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('completion_date', models.DateTimeField(null=True)),
                ('class_type', models.CharField(choices=[('Core_prep', 'Core Prep'), ('CPEA', 'CPEA'), ('Group_class', 'Group Class')], max_length=500)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_student_journey', to='db.appointments')),
            ],
            options={
                'db_table': 'student_journey',
            },
        ),
        migrations.CreateModel(
            name='StudentClasses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('is_cpea_enabled', models.BooleanField(default=False)),
                ('is_core_prep_enabled', models.BooleanField(default=False)),
                ('is_group_class_enabled', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_class', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'student_classes',
            },
        ),
    ]
