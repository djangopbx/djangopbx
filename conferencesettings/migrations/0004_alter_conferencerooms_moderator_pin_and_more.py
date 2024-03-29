# Generated by Django 4.0.4 on 2023-11-16 19:26

import conferencesettings.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conferencesettings', '0003_alter_conferencerooms_moderator_pin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conferencerooms',
            name='moderator_pin',
            field=models.CharField(default=conferencesettings.models.random_pin, max_length=16, verbose_name='Moderator PIN'),
        ),
        migrations.AlterField(
            model_name='conferencerooms',
            name='participant_pin',
            field=models.CharField(default=conferencesettings.models.random_pin, max_length=16, verbose_name='Participant PIN'),
        ),
    ]
