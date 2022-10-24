# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import os
import secrets

from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.html import format_html
from django.utils.timezone import now

from cms.aws_helpers import delete_from_s3, upload
from cms.reusable import create_rss_title
from distributors.models import Distributors
from people.models import People


def upload_movie_photo(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload(instance, instance.photo_file_name, instance.id, "movies", "photos")
    return os.path.join(f"production/movies/photos/{instance.id}/", "original.jpg")


def upload_movie_poster(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload(instance, instance.poster_file_name, instance.id, "movies", "posters")
    return os.path.join(f"production/movies/posters/{instance.id}/", "original.jpg")


# media is not connected by foreign key like rest of models, so pre_delete
# signal is used that deletes media when sender objects are deleted


class Movies(models.Model):
    # added field to the model to connect to the media

    # i know the namings do not make sense - it seems like
    # object_id_field and content_type_field should be other
    # way around, but this is the only way to make old data
    # work in new cms
    """media = GenericRelation(
        Media,
        related_query_name='movie',
        object_id_field='media_connection_type',
        content_type_field='media_connection_id',
    )"""
    # _______________
    id = models.AutoField(primary_key=True)
    original_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    poster_file_name = models.CharField(max_length=255, null=True)
    poster_content_type = models.CharField(max_length=255, blank=True, null=True)
    poster_file_size = models.IntegerField(blank=True, null=True)
    poster_updated_at = models.DateTimeField(blank=True, null=True)

    ignore = models.IntegerField(null=True, default=0)
    imdb_id = models.CharField(max_length=255, null=True)

    photo_file_name = models.CharField(max_length=255, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    rss_title = models.CharField(max_length=255, blank=True, null=True)
    premiere_date = models.CharField(max_length=255, blank=True, null=True)
    imdb_rating = models.CharField(max_length=255, blank=True, null=True)
    tomato_rating = models.FloatField(blank=True, null=True)
    stars_average = models.FloatField(blank=True, null=True)
    stars_count = models.IntegerField(blank=True, null=True)
    watchlist_count = models.IntegerField(blank=True, null=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    tomato_id = models.CharField(max_length=255, blank=True, null=True)
    metacritic_rating = models.FloatField(blank=True, null=True)
    metacritic_id = models.CharField(max_length=255, blank=True, null=True)
    motion_poster_file_name = models.FileField(max_length=255, blank=True, null=True)
    motion_poster_content_type = models.CharField(max_length=255, blank=True, null=True)
    motion_poster_file_size = models.IntegerField(blank=True, null=True)
    motion_poster_updated_at = models.DateTimeField(blank=True, null=True)
    poster_parser_count = models.IntegerField(blank=True, null=True)
    tmdb_id = models.IntegerField(null=True)
    tmdb_popularity = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    budget = models.FloatField(blank=True, null=True)
    revenue = models.FloatField(blank=True, null=True)
    spoken_languages = models.CharField(max_length=255, blank=True, null=True)
    made_in = models.CharField(max_length=255, blank=True, null=True)
    paths_to_posters = models.TextField(blank=True, null=True)
    original_language = models.CharField(max_length=255, blank=True, null=True)
    paths_to_photos = models.TextField(blank=True, null=True)
    locked_attributes = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.original_title:
            return self.original_title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "movies"
        verbose_name = "Movie"
        verbose_name_plural = "Movies"

    def poster_tag(self):
        if self.poster_file_name or self.paths_to_posters:
            return format_html(
                '<img src="{}?{}" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/"
                    f"movies/posters/{self.id}/tiny.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Poster not added."

    poster_tag.short_description = "Poster"  # type: ignore
    poster_tag.allow_tags = True  # type: ignore

    def photo_tag(self):
        if self.photo_file_name or self.paths_to_photos:
            return format_html(
                '<img src="{}?{}" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/"
                    f"movies/photos/{self.id}/tiny.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Photo not added."

    photo_tag.short_description = "Photo"  # type: ignore
    photo_tag.allow_tags = True  # type: ignore


@receiver(pre_delete, sender=Movies)
def delete_movies(sender, instance, **kwargs):
    delete_from_s3(instance, instance.id, "movies", "posters")
    delete_from_s3(instance, instance.id, "movies", "photos")


@receiver(post_save, sender=Movies)
def create_info(sender, instance, **kwargs):
    movie_id = instance.id
    rss_title = create_rss_title(instance.original_title)
    if instance.rss_title is None or instance.rss_title == "":
        instance.rss_title = rss_title
        instance.save()

    info = Infos.objects.filter(movie_id=movie_id).first()
    rss_title = create_rss_title(instance.original_title)
    if not info:
        Infos.objects.create(
            movie_id=movie_id,
            locale="de",
            summary="Noch keine Beschreibung",
            rss_title=rss_title,
        )


RATING_CHOICES = ((0, 0), (6, 6), (12, 12), (16, 16), (18, 18), ("", ""))


def upload_info_poster(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload(instance, instance.poster_file_name, instance.id, "infos", "posters")
    return os.path.join(f"production/infos/posters/{instance.id}/", "original.jpg")


class Infos(models.Model):
    # added field to the model to connect to the media
    """media = GenericRelation(
        Media,
        related_query_name='info',
        object_id_field='media_connection_type',
        content_type_field='media_connection_id',
    )"""
    # _______________
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(
        Movies, on_delete=models.CASCADE, db_column="movie_id", related_name="infos"
    )
    locale = models.CharField(max_length=255, blank=True, null=True)
    premiere_date = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=255, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    duration = models.CharField(max_length=255, blank=True, null=True)
    rss_title = models.CharField(max_length=255, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    directors = models.CharField(max_length=255, blank=True, null=True)
    poster_file_name = models.CharField(max_length=255, null=True)
    poster_content_type = models.CharField(max_length=255, blank=True, null=True)
    poster_file_size = models.IntegerField(blank=True, null=True)
    poster_updated_at = models.DateTimeField(blank=True, null=True)
    popularity = models.DecimalField(
        max_digits=18, decimal_places=12, blank=True, null=True
    )
    coming_soon = models.IntegerField(blank=True, null=True, default=0)
    showtimes_count = models.IntegerField(blank=True, null=True)
    stars_count = models.IntegerField(blank=True, null=True)
    stars_average = models.FloatField(blank=True, null=True)
    watchlist_count = models.IntegerField(blank=True, null=True)
    coming_soon_position = models.IntegerField(blank=True, null=True)
    popularity_date_until = models.DateTimeField(blank=True, null=True)
    pg_rating = models.IntegerField(blank=True, null=True, choices=RATING_CHOICES)
    alternative_version = models.IntegerField(blank=True, null=True, default=0)
    paths_to_posters = models.TextField(blank=True, null=True)
    tracking_id = models.CharField(max_length=255, blank=True, null=True)
    distributor = models.ForeignKey(
        Distributors,
        on_delete=models.CASCADE,
        db_column="distributor_id",
        related_name="infos",
        blank=True,
        null=True,
    )
    locked_attributes = models.TextField(blank=True, null=True)
    at_premiere_date = models.DateField(blank=True, null=True)
    at_coming_soon = models.IntegerField(blank=True, null=True)
    at_distributor_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "infos"
        verbose_name = "Info"
        verbose_name_plural = "Infos"

    def poster_tag(self):
        if self.poster_file_name or self.paths_to_posters:
            return format_html(
                '<img src="{}?{}" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/"
                    f"infos/posters/{self.id}/tiny.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Poster not added."

    poster_tag.short_description = "Poster"  # type: ignore
    poster_tag.allow_tags = True  # type: ignore


@receiver(pre_delete, sender=Infos)
def delete_infos(sender, instance, **kwargs):
    delete_from_s3(instance, instance.id, "infos", "posters")


@receiver(post_save, sender=Infos)
def create_rss_title_for_infos(sender, instance, **kwargs):
    rss_title = create_rss_title(instance.title)
    if instance.rss_title is None or instance.rss_title == "":
        instance.rss_title = rss_title
        instance.save()


class InfosWithShowtimes(Infos):
    class Meta:
        proxy = True
        verbose_name = "Info with Showtimes"
        verbose_name_plural = "Infos with Showtimes"


class InfosWithHotShowtimes(Infos):
    class Meta:
        proxy = True
        verbose_name = "Info with Hot Showtimes"
        verbose_name_plural = "Infos with Hot Showtimes"


class AtInfosWithShowtimes(Infos):
    class Meta:
        proxy = True
        verbose_name = "At Info with Showtimes"
        verbose_name_plural = "At Infos with Showtimes"


class ChInfosWithShowtimes(Infos):
    class Meta:
        proxy = True
        verbose_name = "Ch Info with Showtimes"
        verbose_name_plural = "Ch Infos with Showtimes"


class MoviesPeople(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        db_column="person_id",
        related_name="movie_people",
    )
    movie = models.ForeignKey(
        Movies,
        on_delete=models.CASCADE,
        db_column="movie_id",
        related_name="movie_people",
    )
    person_role = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    order = models.IntegerField(blank=True, null=True)
    character_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.character_name:
            return self.character_name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "movies_people"
        verbose_name = "Movie Person"
        verbose_name_plural = "Movies People"


class MovieAliases(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(
        Movies,
        on_delete=models.CASCADE,
        db_column="movie_id",
        related_name="movie_aliases",
    )
    original_title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.original_title:
            return self.original_title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "movie_aliases"
        verbose_name = "Movie Alias"
        verbose_name_plural = "Movies Aliases"


class InfoAliases(models.Model):
    id = models.AutoField(primary_key=True)
    info = models.ForeignKey(
        Infos,
        on_delete=models.CASCADE,
        db_column="info_id",
        related_name="info_aliases",
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    locale = models.CharField(default="de", editable=False, max_length=10)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "info_aliases"
        verbose_name = "Info Alias"
        verbose_name_plural = "Infos Aliases"
