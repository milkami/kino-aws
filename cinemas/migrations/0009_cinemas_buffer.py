# Generated by Django 3.2.13 on 2022-08-10 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinemas', '0008_remove_cinemas_setting_group_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='cinemas',
            name='buffer',
            field=models.IntegerField(blank=True, default=20, null=True),
        ),
    ]
