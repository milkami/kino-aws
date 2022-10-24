# Generated by Django 3.1.7 on 2021-03-29 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0003_people"),
    ]

    operations = [
        migrations.CreateModel(
            name="MoviesPeople",
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
                ("person_id", models.IntegerField(blank=True, null=True)),
                ("movie_id", models.IntegerField(blank=True, null=True)),
                (
                    "person_role",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("order", models.IntegerField(blank=True, null=True)),
                (
                    "character_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "verbose_name": "Movie Person",
                "verbose_name_plural": "Movies People",
                "db_table": "movies_people",
                "managed": False,
            },
        ),
    ]