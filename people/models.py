import secrets

from django.db import models
from django.utils.html import format_html
from django.utils.timezone import now


# Create your models here.
class People(models.Model):
    id = models.AutoField(primary_key=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    imdb_id = models.CharField(max_length=255, blank=True, null=True)
    also_known_as = models.CharField(max_length=250, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    deathday = models.DateField(blank=True, null=True)
    homepage = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    place_of_birth = models.CharField(max_length=255, blank=True, null=True)
    popularity = models.FloatField(blank=True, null=True)
    photo_path = models.CharField(max_length=255, blank=True, null=True)
    photo_file_name = models.CharField(max_length=255, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    paths_to_photos = models.TextField(blank=True, null=True)
    show_images = models.IntegerField(blank=True, null=True)
    locked_attributes = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""

    class Meta:
        managed = False
        db_table = "people"
        verbose_name = "Person"
        verbose_name_plural = "People"

    def photo_tag(self):
        if self.photo_file_name or self.paths_to_photos or self.photo_path:
            return format_html(
                '<img src="{}?{}" style="height: 150px;" alt="" />'.format(
                    f"https://kinode.s3-eu-west-1.amazonaws.com/production/"
                    f"people/{self.id}/small.jpg",
                    secrets.randbelow(100000),
                )
            )
        else:
            return "Photo not added."

    photo_tag.short_description = "Photo"  # type: ignore
    photo_tag.allow_tags = True  # type: ignore
