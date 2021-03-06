# Generated by Django 4.0.4 on 2022-05-08 06:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('app_uuid', models.UUIDField(blank=True, editable=False, null=True)),
                ('category', models.CharField(max_length=32, verbose_name='Category')),
                ('subcategory', models.CharField(max_length=32, verbose_name='Subcategory')),
                ('value_type', models.CharField(choices=[('text', 'text'), ('numeric', 'numeric'), ('array', 'array'), ('boolean', 'boolean'), ('code', 'code'), ('uuid', 'uuid'), ('name', 'name'), ('var', 'var'), ('dir', 'dir')], default='text', max_length=32, verbose_name='Type')),
                ('value', models.CharField(blank=True, max_length=254, null=True, verbose_name='Value')),
                ('sequence', models.DecimalField(decimal_places=0, default=10, max_digits=11, verbose_name='Order')),
                ('enabled', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
            ],
            options={
                'db_table': 'pbx_default_settings',
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, help_text='Eg. tenant.djangopbx.com', max_length=128, unique=True, verbose_name='Name')),
                ('enabled', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
            ],
            options={
                'db_table': 'pbx_domains',
                'permissions': (('can_select_domain', 'can_select_domain'),),
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('username', models.CharField(db_index=True, max_length=150, unique=True, verbose_name='User ID')),
                ('email', models.CharField(max_length=254, null=True, verbose_name='Email')),
                ('status', models.CharField(blank=True, choices=[('', 'Not Set'), ('Available', 'Available'), ('Available (On Demand)', 'Available (On Demand)'), ('Logged Out', 'Logged Out'), ('On Break', 'On Break'), ('Do Not Disturb', 'Do Not Disturb')], default='', max_length=32, verbose_name='Status')),
                ('api_key', models.CharField(blank=True, max_length=254, null=True, verbose_name='API Key')),
                ('enabled', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Enabled')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tenants.domain', verbose_name='Domain')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'db_table': 'pbx_users',
            },
        ),
        migrations.CreateModel(
            name='ProfileSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=32, verbose_name='Category')),
                ('subcategory', models.CharField(max_length=32, verbose_name='Subcategory')),
                ('value_type', models.CharField(choices=[('text', 'text'), ('numeric', 'numeric'), ('array', 'array'), ('boolean', 'boolean'), ('code', 'code'), ('uuid', 'uuid'), ('name', 'name'), ('var', 'var'), ('dir', 'dir')], default='text', max_length=32, verbose_name='Type')),
                ('value', models.CharField(blank=True, max_length=254, null=True, verbose_name='Value')),
                ('sequence', models.DecimalField(decimal_places=0, default=10, max_digits=11, verbose_name='Order')),
                ('enabled', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.profile', verbose_name='User')),
            ],
            options={
                'db_table': 'pbx_user_settings',
            },
        ),
        migrations.CreateModel(
            name='DomainSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('app_uuid', models.UUIDField(blank=True, editable=False, null=True)),
                ('category', models.CharField(max_length=32, verbose_name='Category')),
                ('subcategory', models.CharField(max_length=32, verbose_name='Subcategory')),
                ('value_type', models.CharField(choices=[('text', 'text'), ('numeric', 'numeric'), ('array', 'array'), ('boolean', 'boolean'), ('code', 'code'), ('uuid', 'uuid'), ('name', 'name'), ('var', 'var'), ('dir', 'dir')], default='text', max_length=32, verbose_name='Type')),
                ('value', models.CharField(blank=True, max_length=254, null=True, verbose_name='Value')),
                ('sequence', models.DecimalField(decimal_places=0, default=10, max_digits=11, verbose_name='Order')),
                ('enabled', models.CharField(choices=[('true', 'True'), ('false', 'False')], default='true', max_length=8, verbose_name='Enabled')),
                ('description', models.CharField(blank=True, max_length=128, null=True, verbose_name='Description')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
                ('domain_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.domain', verbose_name='Domain')),
            ],
            options={
                'db_table': 'pbx_domain_settings',
            },
        ),
    ]
