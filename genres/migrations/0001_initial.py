# Generated by Django 3.1.7 on 2021-03-27 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="GenreAliases",
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
                ("genre_id", models.IntegerField(blank=True, null=True)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "verbose_name": "Genre Alias",
                "verbose_name_plural": "Genre Aliases",
                "db_table": "genre_aliases",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Genres",
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
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("alias_name", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "verbose_name": "Genre",
                "verbose_name_plural": "Genres",
                "db_table": "genres",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="GenresMovies",
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
                ("genre_id", models.IntegerField(blank=True, null=True)),
                ("movie_id", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "verbose_name": "Genres Movie",
                "verbose_name_plural": "Genres Movies",
                "db_table": "genres_movies",
                "managed": False,
            },
        ),
    ]