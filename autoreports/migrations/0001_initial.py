# Generated by Django 4.0.4 on 2023-12-23 09:51

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
            name='AutoReports',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Report')),
                ('name', models.CharField(blank=True, max_length=64, null=True, verbose_name='Name')),
                ('title', models.CharField(blank=True, max_length=128, null=True, verbose_name='Title')),
                ('message', models.TextField(blank=True, help_text='Enter any message to be show with the report.  Eg. Company address', null=True, verbose_name='Message')),
                ('footer', models.CharField(blank=True, help_text='Appears in small print at the end of the report', max_length=256, null=True, verbose_name='Footer')),
                ('recipients', models.TextField(help_text='Enter email addresses, one per line', verbose_name='Recipients')),
                ('frequency', models.CharField(blank=True, choices=[('month', 'Monthly'), ('week', 'Weekly'), ('day', 'Daily'), ('hour', 'Hourly')], default='week', max_length=8, null=True, verbose_name='Frequency')),
                ('enabled', models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(blank=True, db_column='domain_uuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.domain', verbose_name='Domain')),
            ],
            options={
                'verbose_name_plural': 'Auto Report',
                'db_table': 'pbx_auto_report',
            },
        ),
        migrations.CreateModel(
            name='AutoReportSections',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Report')),
                ('title', models.CharField(blank=True, max_length=128, null=True, verbose_name='(sub) Title')),
                ('sequence', models.DecimalField(decimal_places=0, default=10, max_digits=3, verbose_name='Sequence')),
                ('sql', models.TextField(help_text='Enter the SQL query for this report section', verbose_name='SQL')),
                ('message', models.TextField(blank=True, help_text='Notes about this section for the customer', null=True, verbose_name='Message')),
                ('enabled', models.CharField(choices=[('false', 'False'), ('true', 'True')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('auto_report_id', models.ForeignKey(blank=True, db_column='auto_report_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='autoreports.autoreports', verbose_name='Report')),
            ],
            options={
                'verbose_name_plural': 'Auto Report Section',
                'db_table': 'pbx_auto_report_section',
            },
        ),
    ]
