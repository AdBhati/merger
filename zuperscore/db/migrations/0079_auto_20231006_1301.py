# Generated by Django 3.2.20 on 2023-10-06 07:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0078_rename_sub_topic_agenda_subtopic'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agenda',
            old_name='subtopic',
            new_name='topic',
        ),
        migrations.AddField(
            model_name='mothersessionplan',
            name='megadomain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='db.megadomain'),
        ),
        migrations.AlterModelTable(
            name='agenda',
            table='agendas',
        ),
    ]
