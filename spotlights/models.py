# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import os
from datetime import date, datetime, timedelta

from django.db import models
from django.utils.timezone import now

from cms.aws_helpers import upload_spotlights

SPOTLIGHT_TYPE_CHOICES = (
    ("coming_soon", "coming_soon"),
    ("in_cinemas", "in_cinemas"),
    ("on_demand", "on_demand"),
    ("tv_shows", "tv_shows"),
    ("movie_trailer", "movie_trailer"),
    ("tv_show_trailer", "tv_show_trailer"),
    ("list", "list"),
    ("person", "person"),
    ("ad", "ad"),
    ("", ""),
)

# home_tab, in_cinemas_tab, coming_soon_tab, on_demand_tab, tv_shows_tab.

LOCATION_CHOICES = (
    ("home_tab", "home_tab"),
    ("in_cinemas_tab", "in_cinemas_tab"),
    ("coming_soon_tab", "coming_soon_tab"),
    ("on_demand_tab", "on_demand_tab"),
    ("tv_shows_tab", "tv_shows_tab"),
    ("", ""),
)


def thursday():
    today = date.today()
    start_date = today + timedelta(days=(3 - today.weekday()))
    current_week = start_date + timedelta(days=7)
    to_date = datetime(
        year=current_week.year, month=current_week.month, day=current_week.day, hour=8
    )
    from_date = datetime(
        year=start_date.year, month=start_date.month, day=start_date.day, hour=8
    )
    return from_date, to_date


def upload_56_portrait(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload_spotlights(
        instance,
        instance.background_56_portrait_file_name,
        "spotlights",
        "background_56_portraits",
    )
    return os.path.join(
        f"production/spotlights/{instance.id}/background_56_portraits/", "original.jpg"
    )


def upload_75_portrait(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload_spotlights(
        instance,
        instance.background_75_portrait_file_name,
        "spotlights",
        "background_75_portraits",
    )
    return os.path.join(
        f"production/spotlights/{instance.id}/background_75_portraits/", "original.jpg"
    )


def upload_75_landscape(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload_spotlights(
        instance,
        instance.background_75_landscape_file_name,
        "spotlights",
        "background_75_landscapes",
    )
    return os.path.join(
        f"production/spotlights/{instance.id}/background_75_landscapes/", "original.jpg"
    )


class Spotlights(models.Model):
    id = models.AutoField(primary_key=True)
    spotlight_type = models.CharField(max_length=255, choices=SPOTLIGHT_TYPE_CHOICES)
    position = models.IntegerField(verbose_name="#")
    available_from = models.DateTimeField(default=thursday()[0])
    available_until = models.DateTimeField(default=thursday()[1])
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    background_56_portrait_file_name = models.CharField(max_length=255, null=True)
    background_56_portrait_content_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    background_56_portrait_file_size = models.IntegerField(blank=True, null=True)
    background_56_portrait_updated_at = models.DateTimeField(blank=True, null=True)
    video_56_portrait_file_name = models.CharField(max_length=255, null=True)
    video_56_portrait_content_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    video_56_portrait_file_size = models.IntegerField(blank=True, null=True)
    video_56_portrait_updated_at = models.DateTimeField(blank=True, null=True)
    background_75_portrait_file_name = models.CharField(max_length=255, null=True)
    background_75_portrait_content_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    background_75_portrait_file_size = models.IntegerField(blank=True, null=True)
    background_75_portrait_updated_at = models.DateTimeField(blank=True, null=True)
    background_75_landscape_file_name = models.CharField(max_length=255, null=True)
    background_75_landscape_content_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    background_75_landscape_file_size = models.IntegerField(blank=True, null=True)
    background_75_landscape_updated_at = models.DateTimeField(blank=True, null=True)
    target_id = models.IntegerField()
    target_link = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, choices=LOCATION_CHOICES)
    photo_file_name = models.FileField(max_length=255, blank=True, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "spotlights"
        verbose_name = "Spotlight"
        verbose_name_plural = "Spotlights"
