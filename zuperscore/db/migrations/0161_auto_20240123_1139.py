# Generated by Django 3.2.20 on 2024-01-23 06:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0160_auto_20240122_2039'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnglishStudentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('baseline_score', models.CharField(default='<550', max_length=20)),
                ('ca', models.CharField(choices=[('2ca', '2 CA'), ('3ca', '3 CA'), ('4ca', '4 CA')], default='2ca', max_length=20)),
                ('ha', models.CharField(choices=[('5ha', '5 HA'), ('6ha', '6 HA'), ('7ha', '7 HA')], default='5ha', max_length=20)),
                ('name', models.CharField(choices=[('r', 'R'), ('s', 'S'), ('t', 'T')], default='r', max_length=20)),
                ('difficulty', models.CharField(default='5', max_length=20)),
                ('short_desc', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'english_student_category',
            },
        ),
        migrations.CreateModel(
            name='MathStudentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('baseline_score', models.CharField(default='<550', max_length=20)),
                ('ca', models.CharField(choices=[('2ca', '2 CA'), ('3ca', '3 CA'), ('4ca', '4 CA')], default='2ca', max_length=20)),
                ('ha', models.CharField(choices=[('5ha', '5 HA'), ('6ha', '6 HA'), ('7ha', '7 HA')], default='5ha', max_length=20)),
                ('name', models.CharField(choices=[('r', 'R'), ('s', 'S'), ('t', 'T')], default='r', max_length=20)),
                ('difficulty', models.CharField(default='5', max_length=20)),
                ('short_desc', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'math_student_category',
            },
        ),
        migrations.RemoveField(
            model_name='user',
            name='category',
        ),
        migrations.AddField(
            model_name='user',
            name='english_student_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='english_student_category', to='db.englishstudentcategory'),
        ),
        migrations.AddField(
            model_name='user',
            name='math_student_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='math_student_category', to='db.mathstudentcategory'),
        ),
    ]
