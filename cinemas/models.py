# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import secrets
from datetime import datetime, time, timedelta

from django.contrib import messages
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.html import format_html
from django.utils.timezone import now

from movies.models import Infos, Movies
# from other.models import SettingGroups
from datetime import timedelta, datetime, time
from movies.models import Infos


class MoviePlaylist(Infos):
    class Meta:
        proxy = True
        verbose_name = "Movie in Playlist"
        verbose_name_plural = "Movies in Playlist"


class Chains(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    tos_url = models.TextField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    # setting_group = models.ForeignKey(
    #     SettingGroups,
    #     on_delete=models.CASCADE,
    #     db_column="setting_group_id",
    #     related_name="chains",
    # )

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "chains"
        verbose_name = "Chain"
        verbose_name_plural = "Chains"


TYPE_CHOICES = (
    ("cinema", "cinema"),
    ("occasional", "occasional"),
    ("open-air", "open-air"),
    ("mobile", "mobile"),
    ("", ""),
)


class Cinemas(models.Model):
    id = models.AutoField(primary_key=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    default_ticket_url = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=255, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    short_name = models.CharField(max_length=255, blank=True, null=True)
    chain = models.ForeignKey(
        Chains,
        on_delete=models.CASCADE,
        db_column="chain_id",
        related_name="cinemas",
        null = True,
    )
    api_name = models.CharField(max_length=255, blank=True, null=True)
    cinema_parser_id = models.IntegerField(blank=True, null=True)
    kinode_id = models.IntegerField(blank=True, null=True)
    cinepass_id = models.CharField(max_length=255, blank=True, null=True)
    confirm_date = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    kinode_app_id = models.CharField(max_length=255, blank=True, null=True)
    # setting_group_id = models.IntegerField(blank=True, null=True)
    kinoheld_id = models.CharField(max_length=255, blank=True, null=True)
    kranki_id = models.CharField(max_length=255, blank=True, null=True)
    default_url = models.CharField(max_length=255, blank=True, null=True)
    cinema_type = models.CharField(
        max_length=255, blank=True, null=True, choices=TYPE_CHOICES
    )
    buffer = models.IntegerField(blank=True, null=True, default=20)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "cinemas"
        verbose_name = "Cinema"
        verbose_name_plural = "Cinemas"


class NewKinoheldCinemas(Cinemas):
    class Meta:
        proxy = True
        verbose_name = "New Kinoheld Cinema"
        verbose_name_plural = "New Kinoheld Cinemas"


class RemovedKinoheldCinemas(Cinemas):
    class Meta:
        proxy = True
        verbose_name = "Removed Kinoheld Cinema"
        verbose_name_plural = "Removed Kinoheld Cinemas"


# class Kinoheld(Cinemas):
#     class Meta:
#         proxy = True
#         verbose_name = "Compare Kinoheld"
#         verbose_name_plural = "Compare Kinoheld"


class CinemaParsers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    legacy = models.IntegerField(blank=True, null=True)
    reservation = models.IntegerField(blank=True, null=True)
    purchase = models.IntegerField(blank=True, null=True)
    paypal = models.IntegerField(blank=True, null=True)
    master = models.IntegerField(blank=True, null=True)
    visa = models.IntegerField(blank=True, null=True)
    amex = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    instructions_file_name = models.CharField(max_length=255, blank=True, null=True)
    instructions_content_type = models.CharField(max_length=255, blank=True, null=True)
    instructions_file_size = models.IntegerField(blank=True, null=True)
    instructions_updated_at = models.DateTimeField(blank=True, null=True)
    custom_attributes = models.TextField(blank=True, null=True)
    purchase_qr_code = models.IntegerField(blank=True, null=True)
    reservation_qr_code = models.IntegerField(blank=True, null=True)
    ec_maestro = models.IntegerField(blank=True, null=True)
    tester = models.IntegerField(blank=True, null=True)
    developer = models.IntegerField(blank=True, null=True)
    # setting_group_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "cinema_parsers"
        verbose_name = "Cinema Parser"
        verbose_name_plural = "Cinema Parsers"


class Parsers(models.Model):
    id = models.AutoField(primary_key=True)
    cinema = models.ForeignKey(
        Cinemas, on_delete=models.CASCADE, db_column="cinema_id", related_name="parsers"
    )
    rss_address = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    last_log = models.TextField(blank=True, null=True)
    error_log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    parser_type = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    night_queue = models.IntegerField(blank=True, null=True)
    in_app_booking = models.IntegerField(blank=True, null=True)
    hour_queue = models.IntegerField(blank=True, null=True)
    custom_attributes = models.TextField(blank=True, null=True)
    queue = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.parser_type:
            return self.parser_type
        else:
            return ""

    class Meta:
        managed = False
        db_table = "parsers"
        verbose_name = "Parser"
        verbose_name_plural = "Parsers"


VALUE_CHOICES = (
    ("3D", "3D"),
    ("4D", "4D"),
    ("OMU", "OmU"),
    ("OMEU", "OmeU"),
    ("OV", "OV"),
    ("", ""),
)


class Showtimes(models.Model):
    id = models.AutoField(primary_key=True)
    info = models.ForeignKey(
        Infos, on_delete=models.CASCADE, db_column="info_id", related_name="showtimes"
    )
    cinema = models.ForeignKey(
        Cinemas,
        on_delete=models.CASCADE,
        db_column="cinema_id",
        related_name="showtimes",
    )
    date = models.DateTimeField(
        blank=True, null=True
    )  # changed from datetime to date, time kept in DB
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    hours = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    value = models.CharField(
        max_length=255, blank=True, null=True, choices=VALUE_CHOICES
    )
    parser = models.IntegerField(blank=True, null=True)
    ticket_link = models.CharField(max_length=255, blank=True, null=True)
    in_app_booking = models.IntegerField(blank=True, null=True)
    movie = models.ForeignKey(
        Movies, on_delete=models.CASCADE, db_column="movie_id", related_name="showtimes"
    )
    parser_type = models.CharField(max_length=255, blank=True, null=True)
    flagged_for_delete = models.IntegerField(blank=True, null=True)
    booking_link = models.CharField(max_length=255, blank=True, null=True)
    flagged_for_overwrite = models.IntegerField(blank=True, null=True)

    def poster_tag(self):
        poster = Infos.objects.get(id=self.info_id).poster_file_name
        if poster:
            return format_html(
                '<img src="{}?{}" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/"
                    f"infos/posters/{self.info_id}/tiny.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Poster not added."

    poster_tag.short_description = "Poster"  # type: ignore
    poster_tag.allow_tags = True  # type: ignore

    class Meta:
        managed = False
        db_table = "showtimes"
        verbose_name = "Showtime"
        verbose_name_plural = "Showtimes"


@receiver(pre_save, sender=Showtimes)
def multiple_datetime_showtimes(sender, instance, **kwargs):
    start_date = instance.start_date
    end_date = instance.end_date
    hours = instance.hours
    if start_date and end_date and hours:
        dates_delta = end_date - start_date
        all_hours = hours.replace(" ", "").split(",")
        datetime_list = []
        for hour in all_hours:
            cur_hours = int(hour.split(":")[0])
            cur_minutes = int(hour.split(":")[1])
            for i in range(dates_delta.days + 1):
                day = start_date + timedelta(days=i)
                date = datetime.combine(
                    day, time(hour=cur_hours, minute=cur_minutes)
                ).astimezone()
                datetime_list.append(date)
        for dt in datetime_list[::-1]:
            original_obj = instance
            original_obj.pk = None
            original_obj.id = None
            original_obj.date = dt
            original_obj.start_date = None
            original_obj.end_date = None
            original_obj.hours = None
            original_obj.save()
        instance.date = datetime_list[0]
        instance.start_date = None
        instance.end_date = None
        instance.hours = None
