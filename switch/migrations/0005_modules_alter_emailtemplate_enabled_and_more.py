# Generated by Django 4.0.4 on 2022-12-08 08:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('switch', '0004_alter_emailtemplate_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='Modules',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Module')),
                ('label', models.CharField(max_length=64, verbose_name='Label')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('category', models.CharField(choices=[('Streams / Files', 'Streams / Files'), ('File Format Interfaces', 'File Format Interfaces'), ('Auto', 'Auto'), ('Say', 'Say'), ('Loggers', 'Loggers'), ('Languages', 'Languages'), ('XML Interfaces', 'XML Interfaces'), ('Speech Recognition / Text to Speech', 'Speech Recognition / Text to Speech'), ('Codecs', 'Codecs'), ('Endpoints', 'Endpoints'), ('Applications', 'Applications'), ('Dialplan Interfaces', 'Dialplan Interfaces'), ('Event Handlers', 'Event Handlers'), ('Other', 'Other')], default='Applications', max_length=64, verbose_name='Category')),
                ('sequence', models.DecimalField(decimal_places=0, default=10, max_digits=11, verbose_name='Order')),
                ('enabled', models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled')),
                ('default_enabled', models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=254, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
            ],
            options={
                'db_table': 'pbx_modules',
            },
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='enabled',
            field=models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled'),
        ),
        migrations.AlterField(
            model_name='sipprofile',
            name='enabled',
            field=models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled'),
        ),
        migrations.AlterField(
            model_name='sipprofilesetting',
            name='enabled',
            field=models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled'),
        ),
        migrations.AlterField(
            model_name='switchvariable',
            name='enabled',
            field=models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled'),
        ),
    ]
