# Generated by Django 4.0.4 on 2022-11-10 07:10

from django.db import migrations, models
import django.db.models.deletion
import pbx.commonwidgets
import recordings.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Recording')),
                ('filename', pbx.commonwidgets.PbxFileField(upload_to=recordings.models.user_directory_path, verbose_name='File Name')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('base64', models.TextField(blank=True, null=True, verbose_name='Base64')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(blank=True, db_column='domain_uuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.domain', verbose_name='Domain')),
            ],
            options={
                'db_table': 'pbx_recordings',
                'permissions': (('can_download_recording', 'can_download_recording'), ('can_upload_recording', 'can_upload_recording'), ('can_play_recording', 'can_play_recording')),
            },
        ),
    ]