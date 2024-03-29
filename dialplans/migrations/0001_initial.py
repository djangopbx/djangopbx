# Generated by Django 4.0.4 on 2022-11-06 17:30

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dialplan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Dialplan')),
                ('app_id', models.UUIDField(blank=True, null=True, verbose_name='AppUuid')),
                ('hostname', models.CharField(blank=True, max_length=128, null=True, verbose_name='Hostname')),
                ('context', models.CharField(blank=True, max_length=128, null=True, verbose_name='Context')),
                ('category', models.CharField(blank=True, default='Dialplan', max_length=32, null=True, verbose_name='Category')),
                ('name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Name')),
                ('number', models.CharField(blank=True, max_length=32, null=True, verbose_name='Number')),
                ('destination', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Destination')),
                ('dp_continue', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='false', max_length=8, verbose_name='Continue')),
                ('xml', models.TextField(blank=True, null=True, verbose_name='Xml')),
                ('sequence', models.DecimalField(decimal_places=0, default=200, max_digits=3, verbose_name='Order')),
                ('enabled', models.CharField(blank=True, choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=254, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.domain', verbose_name='Domain')),
            ],
            options={
                'db_table': 'pbx_dialplans',
            },
        ),
        migrations.CreateModel(
            name='DialplanDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='DialplanDetail')),
                ('tag', models.CharField(choices=[('condition', 'Condition'), ('regex', 'Regular Expression'), ('action', 'Action'), ('anti-action', 'Anti Action')], default='condition', max_length=32, verbose_name='Tag')),
                ('type', models.CharField(max_length=32, verbose_name='Type')),
                ('data', models.CharField(blank=True, max_length=128, null=True, verbose_name='Data')),
                ('dp_break', models.CharField(blank=True, choices=[('', 'Not Set'), ('on-true', 'On True'), ('on-false', 'On False'), ('always', 'Always'), ('never', 'Never')], default='', max_length=8, null=True, verbose_name='Break')),
                ('inline', models.CharField(blank=True, choices=[('', 'Not Set'), ('true', 'True'), ('false', 'False')], default='', max_length=8, null=True, verbose_name='Inline')),
                ('group', models.DecimalField(decimal_places=0, default=0, max_digits=11, verbose_name='Group')),
                ('sequence', models.DecimalField(decimal_places=0, default=10, max_digits=11, verbose_name='Order')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('dialplan_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dialplans.dialplan', verbose_name='Dialplan')),
            ],
            options={
                'db_table': 'pbx_dialplan_details',
            },
        ),
    ]
