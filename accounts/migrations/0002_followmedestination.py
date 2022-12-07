# Generated by Django 4.0.4 on 2022-11-19 10:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowMeDestination',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Extension User')),
                ('destination', models.CharField(max_length=32, verbose_name='Destination')),
                ('delay', models.DecimalField(decimal_places=0, default=0, max_digits=3, verbose_name='Delay')),
                ('timeout', models.DecimalField(decimal_places=0, default=30, max_digits=3, verbose_name='Timeout')),
                ('prompt', models.CharField(blank=True, choices=[('', ''), ('1', 'Confirm')], default='', max_length=8, null=True, verbose_name='Prompt')),
                ('sequence', models.DecimalField(blank=True, decimal_places=0, default=10, max_digits=11, null=True, verbose_name='Order')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('synchronised', models.DateTimeField(blank=True, null=True, verbose_name='Synchronised')),
                ('updated_by', models.CharField(max_length=64, verbose_name='Updated by')),
            ],
            options={
                'db_table': 'pbx_follow_me_destinations',
            },
        ),
    ]