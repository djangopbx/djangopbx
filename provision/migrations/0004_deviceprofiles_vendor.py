# Generated by Django 4.0.4 on 2023-04-29 18:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('provision', '0003_remove_deviceprofilesettings_device_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deviceprofiles',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='provision.devicevendors', verbose_name='Vendor'),
        ),
    ]
