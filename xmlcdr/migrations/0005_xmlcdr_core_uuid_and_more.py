# Generated by Django 5.0.1 on 2024-05-28 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xmlcdr', '0004_alter_calltimeline_call_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='xmlcdr',
            name='core_uuid',
            field=models.UUIDField(blank=True, null=True, verbose_name='Core UUID'),
        ),
        migrations.AlterField(
            model_name='calltimeline',
            name='caller_destination',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, verbose_name='Destination'),
        ),
        migrations.AlterField(
            model_name='calltimeline',
            name='caller_id_number',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, verbose_name='Caller ID Number'),
        ),
        migrations.AlterField(
            model_name='calltimeline',
            name='context',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True, verbose_name='Context'),
        ),
    ]
