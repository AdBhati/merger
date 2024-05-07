# Generated by Django 3.2.20 on 2023-10-06 07:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0079_auto_20231006_1301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chaptertopic',
            name='module',
        ),
        migrations.RemoveField(
            model_name='modulecategorytime',
            name='module',
        ),
        migrations.RemoveField(
            model_name='modulecategorytime',
            name='student_category',
        ),
        migrations.RemoveField(
            model_name='modules',
            name='chapter',
        ),
        migrations.RemoveField(
            model_name='studentchapters',
            name='student',
        ),
        migrations.RemoveField(
            model_name='studentchapters',
            name='student_session_plan',
        ),
        migrations.RemoveField(
            model_name='studentmodules',
            name='student',
        ),
        migrations.RemoveField(
            model_name='studentmodules',
            name='student_chapter',
        ),
        migrations.RemoveField(
            model_name='studentsessionplan',
            name='mother_session_plan',
        ),
        migrations.RemoveField(
            model_name='studentsessionplan',
            name='student',
        ),
        migrations.RemoveField(
            model_name='studentsessionplan',
            name='student_category',
        ),
        migrations.RemoveField(
            model_name='studenttopics',
            name='student',
        ),
        migrations.RemoveField(
            model_name='studenttopics',
            name='student_module',
        ),
        migrations.DeleteModel(
            name='Chapters',
        ),
        migrations.DeleteModel(
            name='ChapterTopic',
        ),
        migrations.DeleteModel(
            name='ModuleCategoryTime',
        ),
        migrations.DeleteModel(
            name='Modules',
        ),
        migrations.DeleteModel(
            name='StudentChapters',
        ),
        migrations.DeleteModel(
            name='StudentModules',
        ),
        migrations.DeleteModel(
            name='StudentSessionPlan',
        ),
        migrations.DeleteModel(
            name='StudentTopics',
        ),
    ]
