# Generated by Django 3.1.7 on 2021-03-26 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="Chains",
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
                ("locale", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                ("tos_url", models.TextField(blank=True, null=True)),
                ("priority", models.IntegerField(blank=True, null=True)),
                ("setting_group_id", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Chain",
                "verbose_name_plural": "Chains",
                "db_table": "chains",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="CinemaParsers",
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
                ("active", models.IntegerField(blank=True, null=True)),
                ("legacy", models.IntegerField(blank=True, null=True)),
                ("reservation", models.IntegerField(blank=True, null=True)),
                ("purchase", models.IntegerField(blank=True, null=True)),
                ("paypal", models.IntegerField(blank=True, null=True)),
                ("master", models.IntegerField(blank=True, null=True)),
                ("visa", models.IntegerField(blank=True, null=True)),
                ("amex", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                (
                    "instructions_file_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "instructions_content_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("instructions_file_size", models.IntegerField(blank=True, null=True)),
                (
                    "instructions_updated_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("custom_attributes", models.TextField(blank=True, null=True)),
                ("purchase_qr_code", models.IntegerField(blank=True, null=True)),
                ("reservation_qr_code", models.IntegerField(blank=True, null=True)),
                ("ec_maestro", models.IntegerField(blank=True, null=True)),
                ("tester", models.IntegerField(blank=True, null=True)),
                ("developer", models.IntegerField(blank=True, null=True)),
                ("setting_group_id", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Cinema Parser",
                "verbose_name_plural": "Cinema Parsers",
                "db_table": "cinema_parsers",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Cinemas",
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
                ("locale", models.CharField(blank=True, max_length=255, null=True)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                (
                    "default_ticket_url",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("phone", models.CharField(blank=True, max_length=255, null=True)),
                ("post_code", models.CharField(blank=True, max_length=255, null=True)),
                ("active", models.IntegerField(blank=True, null=True)),
                ("city", models.CharField(blank=True, max_length=255, null=True)),
                ("short_name", models.CharField(blank=True, max_length=255, null=True)),
                ("chain_id", models.IntegerField(blank=True, null=True)),
                ("api_name", models.CharField(blank=True, max_length=255, null=True)),
                ("cinema_parser_id", models.IntegerField(blank=True, null=True)),
                ("kinode_id", models.IntegerField(blank=True, null=True)),
                (
                    "cinepass_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("confirm_date", models.DateTimeField(blank=True, null=True)),
                ("note", models.TextField(blank=True, null=True)),
                (
                    "kinode_app_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("setting_group_id", models.IntegerField(blank=True, null=True)),
                (
                    "kinoheld_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("kranki_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "default_url",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "cinema_type",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "verbose_name": "Cinema",
                "verbose_name_plural": "Cinemas",
                "db_table": "cinemas",
                "managed": False,
            },
        ),
    ]
