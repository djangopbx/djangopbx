# Generated by Django 4.0.4 on 2023-11-14 16:07

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0004_alter_defaultsetting_subcategory_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallBlock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Call Flow')),
                ('name', models.CharField(blank=True, help_text='Enter the Caller ID Name to block.', max_length=64, null=True, verbose_name='Name')),
                ('number', models.CharField(blank=True, help_text='Enter the Caller ID Number to block.', max_length=64, null=True, verbose_name='Number')),
                ('block_count', models.DecimalField(decimal_places=0, default=0, help_text='The number of time this number has been blocked', max_digits=6, verbose_name='Block Count')),
                ('app', models.CharField(blank=True, max_length=32, null=True, verbose_name='Action App.')),
                ('data', models.CharField(blank=True, help_text='Set an action for calls from this number', max_length=256, null=True, verbose_name='Action')),
                ('enabled', models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=64, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(blank=True, db_column='domain_uuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.domain', verbose_name='Domain')),
            ],
            options={
                'verbose_name_plural': 'Call Block',
                'db_table': 'pbx_call_block',
            },
        ),
    ]
