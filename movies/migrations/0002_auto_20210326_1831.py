# Generated by Django 3.1.7 on 2021-03-26 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Infos",
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
                ("movie_id", models.IntegerField(blank=True, null=True)),
                ("locale", models.CharField(blank=True, max_length=255, null=True)),
                ("premiere_date", models.DateTimeField(blank=True, null=True)),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("genre", models.CharField(blank=True, max_length=255, null=True)),
                ("summary", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("duration", models.CharField(blank=True, max_length=255, null=True)),
                ("rss_title", models.CharField(blank=True, max_length=255, null=True)),
                ("active", models.IntegerField(blank=True, null=True)),
                ("directors", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "poster_file_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "poster_content_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("poster_file_size", models.IntegerField(blank=True, null=True)),
                ("poster_updated_at", models.DateTimeField(blank=True, null=True)),
                (
                    "popularity",
                    models.DecimalField(
                        blank=True, decimal_places=12, max_digits=18, null=True
                    ),
                ),
                ("coming_soon", models.IntegerField(blank=True, null=True)),
                ("showtimes_count", models.IntegerField(blank=True, null=True)),
                ("stars_count", models.IntegerField(blank=True, null=True)),
                ("stars_average", models.FloatField(blank=True, null=True)),
                ("watchlist_count", models.IntegerField(blank=True, null=True)),
                ("coming_soon_position", models.IntegerField(blank=True, null=True)),
                ("popularity_date_until", models.DateTimeField(blank=True, null=True)),
                ("pg_rating", models.IntegerField(blank=True, null=True)),
                ("alternative_version", models.IntegerField(blank=True, null=True)),
                ("paths_to_posters", models.TextField(blank=True, null=True)),
                (
                    "tracking_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("distributor_id", models.IntegerField(blank=True, null=True)),
                ("locked_attributes", models.TextField(blank=True, null=True)),
                ("at_premiere_date", models.DateField(blank=True, null=True)),
                ("at_coming_soon", models.IntegerField(blank=True, null=True)),
                (
                    "at_distributor_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "verbose_name": "Info",
                "verbose_name_plural": "Infos",
                "db_table": "infos",
                "managed": False,
            },
        ),
        migrations.AlterModelOptions(
            name="movies",
            options={
                "managed": False,
                "verbose_name": "Movie",
                "verbose_name_plural": "Movies",
            },
        ),
    ]
