# Generated by Django 3.1.7 on 2021-04-09 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cinemas", "0003_parsers"),
    ]

    operations = [
        migrations.CreateModel(
            name="Kinoheld",
            fields=[],
            options={
                "verbose_name": "Compare Kinoheld",
                "verbose_name_plural": "Compare Kinoheld",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("cinemas.cinemas",),
        ),
    ]
