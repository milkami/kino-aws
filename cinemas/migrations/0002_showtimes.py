# Generated by Django 3.1.7 on 2021-03-29 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cinemas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Showtimes",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("info_id", models.IntegerField(blank=True, null=True)),
                ("cinema_id", models.IntegerField(blank=True, null=True)),
                ("date", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("value", models.CharField(blank=True, max_length=255, null=True)),
                ("parser", models.IntegerField(blank=True, null=True)),
                (
                    "ticket_link",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("in_app_booking", models.IntegerField(blank=True, null=True)),
                ("movie_id", models.IntegerField(blank=True, null=True)),
                (
                    "parser_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("flagged_for_delete", models.IntegerField(blank=True, null=True)),
                (
                    "booking_link",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("flagged_for_overwrite", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Showtime",
                "verbose_name_plural": "Showtimes",
                "db_table": "showtimes",
                "managed": False,
            },
        ),
    ]
