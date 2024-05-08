# Generated by Django 3.2.13 on 2023-05-10 14:06

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('db', '0041_auto_20230427_0532'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Modified At')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'assessment_tags',
            },
        ),
        migrations.AddField(
            model_name='assessment',
            name='domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessment_domain', to='db.domain'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='exam',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessment_exam', to='db.exam'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='is_extended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='is_tutor_test',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='assessment',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessment_subject', to='db.subject'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessment_topic', to='db.topic'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='assessment_tags', to='db.AssessmentTags'),
        ),
    ]