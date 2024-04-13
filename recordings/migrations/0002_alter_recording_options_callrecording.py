# Generated by Django 5.0.1 on 2024-04-09 13:25

import django.db.models.deletion
import pbx.commonwidgets
import recordings.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0001_initial'),
        ('tenants', '0004_alter_defaultsetting_subcategory_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recording',
            options={'permissions': (('can_download_recording', 'can_download_recording'), ('can_upload_recording', 'can_upload_recording'), ('can_play_recording', 'can_play_recording')), 'verbose_name_plural': 'Recordings'},
        ),
        migrations.CreateModel(
            name='CallRecording',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Call Recording')),
                ('filename', pbx.commonwidgets.PbxFileField(upload_to=recordings.models.call_recording_directory_path, verbose_name='File Name')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('year', models.CharField(max_length=8, verbose_name='Year')),
                ('month', models.CharField(max_length=8, verbose_name='Month')),
                ('day', models.CharField(max_length=8, verbose_name='Day')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(blank=True, db_column='domain_uuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.domain', verbose_name='Domain')),
            ],
            options={
                'verbose_name_plural': 'Call Recordings',
                'db_table': 'pbx_call_recordings',
                'permissions': (('can_download_call_recording', 'can_download_call_recording'), ('can_upload_call_recording', 'can_upload_call_recording'), ('can_play_call_recording', 'can_play_call_recording')),
            },
        ),
    ]