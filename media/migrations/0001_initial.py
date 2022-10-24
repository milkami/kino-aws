# Generated by Django 3.1.7 on 2021-03-29 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="Media",
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
                (
                    "media_connection_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("media_connection_id", models.IntegerField(blank=True, null=True)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "trailer_url",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("popularity", models.FloatField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
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
                    "trailer_language",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("featured", models.IntegerField(blank=True, null=True)),
                (
                    "smb_video_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "smb_video_url",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "smb_preview_image",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("smb_duration", models.IntegerField(blank=True, null=True)),
                ("smb_checked_at", models.DateTimeField(blank=True, null=True)),
                ("active", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Media",
                "verbose_name_plural": "Media",
                "db_table": "media",
                "managed": False,
            },
        ),
    ]
