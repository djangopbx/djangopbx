# Generated by Django 4.0.4 on 2023-12-27 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('provision', '0004_deviceprofiles_vendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devices',
            name='provisioned_ip',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='Provisioned Address'),
        ),
    ]
