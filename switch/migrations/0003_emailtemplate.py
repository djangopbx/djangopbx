# Generated by Django 4.0.4 on 2022-11-26 15:27

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0002_alter_defaultsetting_category_and_more'),
        ('switch', '0002_accesscontrol_accesscontrolnode'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Email Template')),
                ('language', models.CharField(default='en-gb', max_length=8, verbose_name='Language')),
                ('category', models.CharField(max_length=32, verbose_name='Category')),
                ('subcategory', models.CharField(default='default', max_length=32, verbose_name='Sub category')),
                ('subject', models.CharField(blank=True, max_length=8, null=True, verbose_name='Subject')),
                ('type', models.CharField(choices=[('html', 'HTML'), ('text', 'Text')], default='html', max_length=8, verbose_name='Type')),
                ('body', models.TextField(blank=True, null=True, verbose_name='Body')),
                ('enabled', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=254, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.domain', verbose_name='Domain')),
            ],
            options={
                'db_table': 'pbx_email_templates',
            },
        ),
    ]
