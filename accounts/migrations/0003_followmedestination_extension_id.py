# Generated by Django 4.0.4 on 2022-11-19 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_followmedestination'),
    ]

    operations = [
        migrations.AddField(
            model_name='followmedestination',
            name='extension_id',
            field=models.ForeignKey(blank=True, db_column='extension_uuid', null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.extension', verbose_name='Extension'),
        ),
    ]
