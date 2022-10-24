# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils.timezone import now

from movies.models import Movies


class Genres(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    alias_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "genres"
        verbose_name = "Genre"
        verbose_name_plural = "Genres"


class GenreAliases(models.Model):
    id = models.AutoField(primary_key=True)
    genre = models.ForeignKey(
        Genres,
        on_delete=models.CASCADE,
        db_column="genre_id",
        related_name="genre_aliases",
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "genre_aliases"
        verbose_name = "Genre Alias"
        verbose_name_plural = "Genre Aliases"


class GenresMovies(models.Model):
    id = models.AutoField(primary_key=True)
    genre = models.ForeignKey(
        Genres,
        on_delete=models.CASCADE,
        db_column="genre_id",
        related_name="genres_movies",
    )
    movie = models.ForeignKey(
        Movies,
        on_delete=models.CASCADE,
        db_column="movie_id",
        related_name="genres_movies",
    )
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.genre.name:
            return self.genre.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "genres_movies"
        verbose_name = "Genres Movie"
        verbose_name_plural = "Genres Movies"
