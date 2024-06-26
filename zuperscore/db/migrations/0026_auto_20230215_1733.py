# Generated by Django 3.2.13 on 2023-02-15 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0025_alter_assessment_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='question_domain', to='db.domain'),
        ),
        migrations.AddField(
            model_name='question',
            name='exam',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='question_exam', to='db.exam'),
        ),
        migrations.AddField(
            model_name='question',
            name='sub_topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='question_sub_topic', to='db.subtopic'),
        ),
        migrations.AddField(
            model_name='question',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='question_subject', to='db.subject'),
        ),
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='question_topic', to='db.topic'),
        ),
    ]
