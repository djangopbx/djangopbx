# Generated by Django 4.0.4 on 2022-11-26 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('switch', '0003_emailtemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='subject',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Subject'),
        ),
    ]
