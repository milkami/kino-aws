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

LAYOUT_CHOICES = (
    ("default", "default"),
    ("top-left", "top-left"),
    ("bottom-left", "bottom-left"),
    ("", ""),
)


class Lists(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    layout = models.CharField(
        max_length=255, blank=True, null=True, choices=LAYOUT_CHOICES
    )
    active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    de_name = models.CharField(max_length=255)
    popularity = models.FloatField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "lists"
        verbose_name = "List"
        verbose_name_plural = "Lists"


class ListsMovies(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(
        Movies,
        on_delete=models.CASCADE,
        db_column="movie_id",
        related_name="list_movies",
    )
    list = models.ForeignKey(
        Lists, on_delete=models.CASCADE, db_column="list_id", related_name="list_movies"
    )
    position = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        if self.list.name:
            return self.list.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "lists_movies"
        verbose_name = "Lists Movie"
        verbose_name_plural = "Lists Movies"
