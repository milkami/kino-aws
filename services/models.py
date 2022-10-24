# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils.timezone import now

from movies.models import Infos, Movies
from tvshows.models import Seasons, SeasonTranslations, TvShows, TvShowTranslations

SERVICE_CHOICES = (
    ("Purchase", "Purchase"),
    ("Streaming", "Streaming"),
)


class Services(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    web = models.CharField(max_length=255, blank=True, null=True)
    tos = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    active = models.IntegerField(blank=True, null=True)
    service_type = models.CharField(
        max_length=255, blank=True, null=True, choices=SERVICE_CHOICES
    )
    priority = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "services"
        verbose_name = "Service"
        verbose_name_plural = "Services"


class SeasonServices(models.Model):
    id = models.AutoField(primary_key=True)
    tv_show_translation = models.ForeignKey(
        TvShowTranslations,
        on_delete=models.CASCADE,
        db_column="tv_show_translation_id",
        related_name="season_services",
    )
    tv_show = models.ForeignKey(
        TvShows,
        on_delete=models.CASCADE,
        db_column="tv_show_id",
        related_name="season_services",
    )
    service = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        db_column="service_id",
        related_name="season_services",
    )
    service_season_id = models.CharField(max_length=255)
    season = models.ForeignKey(
        Seasons,
        on_delete=models.CASCADE,
        db_column="season_id",
        related_name="season_services",
    )
    season_translation = models.ForeignKey(
        SeasonTranslations,
        on_delete=models.CASCADE,
        db_column="season_translation_id",
        related_name="season_services",
    )
    locale = models.CharField(max_length=255, blank=True, null=True)
    rent_price = models.FloatField(blank=True, null=True)
    buy_price = models.FloatField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    available_from = models.DateTimeField(default=now, blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    flat = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    season_number = models.IntegerField()
    buy_episodes = models.IntegerField(blank=True, null=True)
    prices = models.TextField(blank=True, null=True)
    update_link = models.CharField(max_length=255, blank=True, null=True)
    service_tv_show_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.tv_show.original_title:
            return self.tv_show.original_title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "season_services"
        verbose_name = "Season Service"
        verbose_name_plural = "Season Services"


class MoviesServices(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        db_column="service_id",
        related_name="movie_services",
    )
    movie = models.ForeignKey(
        Movies,
        on_delete=models.CASCADE,
        db_column="movie_id",
        related_name="movie_services",
    )
    info = models.ForeignKey(
        Infos,
        on_delete=models.CASCADE,
        db_column="info_id",
        related_name="movie_services",
    )
    locale = models.CharField(max_length=255, blank=True, null=True)
    rent_price = models.FloatField(blank=True, null=True)
    buy_price = models.FloatField(blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    available_from = models.DateTimeField(default=now, blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    flat = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    prices = models.TextField(blank=True, null=True)
    update_link = models.CharField(max_length=255, blank=True, null=True)
    service_movie_id = models.CharField(max_length=255)

    def __str__(self):
        if self.movie.original_title:
            return self.movie.original_title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "movies_services"
        verbose_name = "Movie Service"
        verbose_name_plural = "Movies Services"
