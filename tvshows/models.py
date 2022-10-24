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
from django.utils.timezone import now

from cms.aws_helpers import delete_from_s3, upload
from people.models import People


def upload_tvshow_photo(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload(instance, instance.photo_file_name, instance.id, "tv_shows", "photos")
    return os.path.join(f"production/tv_shows/photos/{instance.id}/", "original.jpg")


def upload_tvshow_poster(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload(instance, instance.poster_file_name, instance.id, "tv_shows", "posters")
    return os.path.join(f"production/tv_shows/posters/{instance.id}/", "original.jpg")


class TvShows(models.Model):
    id = models.AutoField(primary_key=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    episode_run_time = models.CharField(max_length=255, blank=True, null=True)
    first_air_date = models.DateField(blank=True, null=True)
    last_air_date = models.DateField(blank=True, null=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    homepage = models.CharField(max_length=255, blank=True, null=True)
    in_production = models.IntegerField(blank=True, null=True)
    languages = models.CharField(max_length=255, blank=True, null=True)
    networks = models.TextField(blank=True, null=True)
    number_of_episodes = models.IntegerField(blank=True, null=True)
    number_of_seasons = models.IntegerField(blank=True, null=True)
    made_in = models.CharField(max_length=255, blank=True, null=True)
    original_language = models.CharField(max_length=255, blank=True, null=True)
    original_title = models.CharField(max_length=255)
    tmdb_popularity = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    imdb_id = models.CharField(max_length=255, blank=True, null=True)
    imdb_rating = models.CharField(max_length=255, blank=True, null=True)
    metacritic_id = models.CharField(max_length=255, blank=True, null=True)
    metacritic_rating = models.FloatField(blank=True, null=True)
    photo_file_name = models.CharField(max_length=255, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    poster_file_name = models.CharField(max_length=255, null=True)
    poster_content_type = models.CharField(max_length=255, blank=True, null=True)
    poster_file_size = models.IntegerField(blank=True, null=True)
    poster_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    photo_path = models.CharField(max_length=255, blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    locked_attributes = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.original_title:
            return self.original_title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "tv_shows"
        verbose_name = "Tv Show"
        verbose_name_plural = "Tv Shows"

    """def imdb_id(self):
        from django.utils.html import format_html
        if self.imdb_id:
            return format_html(
                '<a href="https://www.imdb.com/title/%s/">%s</a>'
                    .format(self.imdb_id, self.imdb_id)
            )
        else:
            return None
    imdb_id.short_description = 'Imdb id'
    imdb_id.allow_tags = True
    """

    def poster_tag(self):
        from django.utils.html import format_html

        if self.poster_file_name or self.poster_path:
            return format_html(
                '<img src="{}?{}" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/tv_shows/"
                    f"posters/{self.id}/tiny.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Poster not added."

    poster_tag.short_description = "Poster"  # type: ignore
    poster_tag.allow_tags = True  # type: ignore

    def photo_tag(self):
        from django.utils.html import format_html

        if self.photo_file_name or self.photo_path:
            return format_html(
                '<img src="{}?{}" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/tv_shows/"
                    f"photos/{self.id}/tiny.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Photo not added."

    photo_tag.short_description = "Photo"  # type: ignore
    photo_tag.allow_tags = True  # type: ignore


@receiver(post_save, sender=TvShows)
def create_translation(sender, instance, **kwargs):
    tv_show_id = instance.id
    tv_show_translation = TvShowTranslations.objects.filter(
        tv_show_id=tv_show_id
    ).first()
    if not tv_show_translation:
        TvShowTranslations.objects.create(tv_show_id=tv_show_id, locale="de")


@receiver(pre_delete, sender=TvShows)
def delete_tv_shows(sender, instance, **kwargs):
    delete_from_s3(instance, instance.id, "tv_shows", "posters")
    delete_from_s3(instance, instance.id, "tv_shows", "photos")


RATING_CHOICES = ((0, 0), (6, 6), (12, 12), (16, 16), (18, 18), ("", ""))


def upload_translation_poster(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1
    upload(
        instance,
        instance.poster_file_name,
        instance.id,
        "tv_show_translation",
        "posters",
    )
    return os.path.join(
        f"production/tv_show_translation/posters/{instance.id}/", "original.jpg"
    )


class TvShowTranslations(models.Model):
    id = models.AutoField(primary_key=True)
    tv_show = models.ForeignKey(
        TvShows,
        on_delete=models.CASCADE,
        db_column="tv_show_id",
        related_name="tv_show_translations",
    )
    summary = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255)
    locale = models.CharField(max_length=255, blank=True, null=True)
    pg_rating = models.IntegerField(blank=True, null=True, choices=RATING_CHOICES)
    active = models.IntegerField(blank=True, null=True)
    poster_file_name = models.CharField(max_length=255, null=True)
    poster_content_type = models.CharField(max_length=255, blank=True, null=True)
    poster_file_size = models.IntegerField(blank=True, null=True)
    poster_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    popularity = models.DecimalField(
        max_digits=18, decimal_places=12, blank=True, null=True
    )
    stars_count = models.IntegerField(blank=True, null=True)
    stars_average = models.FloatField(blank=True, null=True)
    watchlist_count = models.IntegerField(blank=True, null=True)
    popularity_date_until = models.DateTimeField(blank=True, null=True)
    locked_attributes = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "tv_show_translations"
        verbose_name = "Tv Show Translation"
        verbose_name_plural = "Tv Show Translations"

    def poster_tag(self):
        from django.utils.html import format_html

        if self.poster_file_name or self.poster_path:
            return format_html(
                '<img src="{}?{}" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/"
                    f"tv_show_translation/posters/{self.id}/tiny.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Poster not added."

    poster_tag.short_description = "Poster"  # type: ignore
    poster_tag.allow_tags = True  # type: ignore


@receiver(pre_delete, sender=TvShowTranslations)
def delete_tv_shows_translation(sender, instance, **kwargs):
    delete_from_s3(instance, instance.id, "tv_show_translation", "posters")


class TvShowPeople(models.Model):
    id = models.AutoField(primary_key=True)
    person = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        db_column="person_id",
        related_name="tv_show_people",
    )
    tv_show = models.ForeignKey(
        TvShows,
        on_delete=models.CASCADE,
        db_column="tv_show_id",
        related_name="tv_show_people",
    )
    person_role = models.CharField(max_length=255, blank=True, null=True)
    character_name = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.character_name:
            return self.character_name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "tv_show_people"
        verbose_name = "Tv Show Person"
        verbose_name_plural = "Tv Show People"


class Seasons(models.Model):
    id = models.AutoField(primary_key=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    tv_show = models.ForeignKey(
        TvShows,
        on_delete=models.CASCADE,
        db_column="tv_show_id",
        related_name="seasons",
    )
    air_date = models.DateField(blank=True, null=True)
    season_number = models.IntegerField(blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    poster_file_name = models.CharField(max_length=255, null=True)
    poster_content_type = models.CharField(max_length=255, blank=True, null=True)
    poster_file_size = models.IntegerField(blank=True, null=True)
    poster_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.season_number:
            return f"Season {self.season_number}"
        else:
            return ""

    class Meta:
        managed = False
        db_table = "seasons"
        verbose_name = "Season"
        verbose_name_plural = "Seasons"


@receiver(pre_delete, sender=Seasons)
def delete_seasons(sender, instance, **kwargs):
    delete_from_s3(instance, instance.id, "seasons", "posters")


@receiver(post_save, sender=Seasons)
def create_seasons_translation(sender, instance, **kwargs):
    seasons_translation = SeasonTranslations.objects.filter(
        season_id=instance.id
    ).first()
    if not seasons_translation:
        SeasonTranslations.objects.create(season_id=instance, locale="de")


class Episodes(models.Model):
    id = models.AutoField(primary_key=True)
    original_title = models.CharField(max_length=255, blank=True, null=True)
    tv_show = models.ForeignKey(
        TvShows,
        on_delete=models.CASCADE,
        db_column="tv_show_id",
        related_name="episodes",
    )
    season = models.ForeignKey(
        Seasons,
        on_delete=models.CASCADE,
        db_column="season_id",
        related_name="episodes",
    )
    season_number = models.IntegerField(blank=True, null=True)
    air_date = models.DateField(blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    episode_number = models.IntegerField(blank=True, null=True)
    imdb_id = models.CharField(max_length=255, blank=True, null=True)
    imdb_rating = models.FloatField(blank=True, null=True)
    photo_path = models.CharField(max_length=255, blank=True, null=True)
    photo_file_name = models.CharField(max_length=255, blank=True, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.episode_number and self.original_title:
            return f"Episode {self.episode_number}: {self.original_title}"
        else:
            return ""

    class Meta:
        managed = False
        db_table = "episodes"
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"


@receiver(pre_delete, sender=Episodes)
def delete_episodes(sender, instance, **kwargs):
    delete_from_s3(instance, instance.id, "episodes", "photos")


class SeasonTranslations(models.Model):
    id = models.AutoField(primary_key=True)
    season_id = models.ForeignKey(
        Seasons,
        on_delete=models.CASCADE,
        db_column="season_id",
        related_name="season_translations",
    )
    summary = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    poster_file_name = models.CharField(max_length=255, blank=True, null=True)
    poster_content_type = models.CharField(max_length=255, blank=True, null=True)
    poster_file_size = models.IntegerField(blank=True, null=True)
    poster_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "season_translations"
        verbose_name = "Season Translation"
        verbose_name_plural = "Seasons Translations"


class EpisodeTranslations(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    episode = models.ForeignKey(
        Episodes,
        on_delete=models.CASCADE,
        db_column="episode_id",
        related_name="episode_translations",
    )
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "episode_translations"
        verbose_name = "Episode Translation"
        verbose_name_plural = "Episodes Translations"


class TvShowAliases(models.Model):
    id = models.AutoField(primary_key=True)
    tv_show = models.ForeignKey(
        TvShows,
        on_delete=models.CASCADE,
        db_column="tv_show_id",
        related_name="tv_show_aliases",
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
        db_table = "tv_show_aliases"
        verbose_name = "Tv Show Alias"
        verbose_name_plural = "Tv Shows Aliases"


class TvShowTranslationAliases(models.Model):
    id = models.AutoField(primary_key=True)
    tv_show_translation = models.ForeignKey(
        TvShowTranslations,
        on_delete=models.CASCADE,
        db_column="tv_show_translation_id",
        related_name="tv_show_translation_aliases",
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=10, default="de", editable=False)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "tv_show_translation_aliases"
        verbose_name = "Tv Show Translation Alias"
        verbose_name_plural = "Tv Show Translations Aliases"
