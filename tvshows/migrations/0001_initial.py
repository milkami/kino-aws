# Generated by Django 3.1.7 on 2021-03-26 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="TvShows",
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
                ("tmdb_id", models.IntegerField(blank=True, null=True)),
                (
                    "episode_run_time",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("first_air_date", models.DateField(blank=True, null=True)),
                ("last_air_date", models.DateField(blank=True, null=True)),
                ("genre", models.CharField(blank=True, max_length=255, null=True)),
                ("homepage", models.CharField(blank=True, max_length=255, null=True)),
                ("in_production", models.IntegerField(blank=True, null=True)),
                ("languages", models.CharField(blank=True, max_length=255, null=True)),
                ("networks", models.TextField(blank=True, null=True)),
                ("number_of_episodes", models.IntegerField(blank=True, null=True)),
                ("number_of_seasons", models.IntegerField(blank=True, null=True)),
                ("made_in", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "original_language",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "original_title",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("tmdb_popularity", models.FloatField(blank=True, null=True)),
                ("status", models.CharField(blank=True, max_length=255, null=True)),
                ("type", models.CharField(blank=True, max_length=255, null=True)),
                ("imdb_id", models.CharField(blank=True, max_length=255, null=True)),
                ("imdb_rating", models.FloatField(blank=True, null=True)),
                (
                    "metacritic_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("metacritic_rating", models.FloatField(blank=True, null=True)),
                (
                    "photo_file_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "photo_content_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("photo_file_size", models.IntegerField(blank=True, null=True)),
                ("photo_updated_at", models.DateTimeField(blank=True, null=True)),
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
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("photo_path", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "poster_path",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("locked_attributes", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Tv Show",
                "verbose_name_plural": "Tv Shows",
                "db_table": "tv_shows",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="TvShowTranslations",
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
                ("tv_show_id", models.IntegerField(blank=True, null=True)),
                ("summary", models.TextField(blank=True, null=True)),
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                ("locale", models.CharField(blank=True, max_length=255, null=True)),
                ("pg_rating", models.IntegerField(blank=True, null=True)),
                ("active", models.IntegerField(blank=True, null=True)),
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
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                (
                    "poster_path",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "popularity",
                    models.DecimalField(
                        blank=True, decimal_places=12, max_digits=18, null=True
                    ),
                ),
                ("stars_count", models.IntegerField(blank=True, null=True)),
                ("stars_average", models.FloatField(blank=True, null=True)),
                ("watchlist_count", models.IntegerField(blank=True, null=True)),
                ("popularity_date_until", models.DateTimeField(blank=True, null=True)),
                ("locked_attributes", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Tv Show Translation",
                "verbose_name_plural": "Tv Show Translations",
                "db_table": "tv_show_translations",
                "managed": False,
            },
        ),
    ]
