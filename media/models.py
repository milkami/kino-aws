# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import os

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.timezone import now

from cms.aws_helpers import delete_from_s3, upload
from cms.trailer_helpers import delete_video
from movies.models import Infos, Movies
from tvshows.models import Seasons, TvShows


def upload_media_photo(instance, filename):
    if not instance.id:
        Model = instance.__class__
        instance.id = Model.objects.order_by("id").last().id + 1

    if instance.media_connection_type == "Movie":
        upload(instance, instance.photo_file_name, instance.id, "movies", "media")
        return os.path.join(f"production/movies/media/{instance.id}/", "original.jpg")
    elif instance.media_connection_type == "Info":
        upload(instance, instance.photo_file_name, instance.id, "infos", "media")
        return os.path.join(f"production/infos/media/{instance.id}/", "original.jpg")
    elif instance.media_connection_type == "TvShow":
        upload(instance, instance.photo_file_name, instance.id, "tv_shows", "media")
        return os.path.join(f"production/tv_shows/media/{instance.id}/", "original.jpg")
    elif instance.media_connection_type == "Season":
        upload(instance, instance.photo_file_name, instance.id, "seasons", "media")
        return os.path.join(f"production/seasons/media/{instance.id}/", "original.jpg")


# media is not connected by foreign key like rest of models, so pre_delete
# signal is used that deletes media when sender objects are deleted
@receiver(pre_delete, sender=Movies)
@receiver(pre_delete, sender=Infos)
@receiver(pre_delete, sender=TvShows)
@receiver(pre_delete, sender=Seasons)
def delete_connected_media(sender, instance, **kwargs):
    media = Media.objects.filter(media_connection_id=instance.id)
    media.delete()


class Media(models.Model):
    id = models.AutoField(primary_key=True)
    media_connection_type = models.CharField(max_length=255, blank=True, null=True)
    media_connection_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    trailer_url = models.CharField(max_length=255, blank=True, null=True)
    popularity = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    photo_file_name = models.CharField(max_length=255, null=True)
    photo_content_type = models.CharField(max_length=255, blank=True, null=True)
    photo_file_size = models.IntegerField(blank=True, null=True)
    photo_updated_at = models.DateTimeField(blank=True, null=True)
    trailer_language = models.CharField(max_length=255, blank=True, null=True)
    featured = models.IntegerField(blank=True, null=True)
    smb_video_id = models.CharField(max_length=255, blank=True, null=True)
    smb_video_url = models.CharField(max_length=255, blank=True, null=True)
    smb_preview_image = models.CharField(max_length=255, blank=True, null=True)
    smb_duration = models.IntegerField(blank=True, null=True)
    smb_checked_at = models.DateTimeField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "media"
        verbose_name = "Media"
        verbose_name_plural = "Media"


@receiver(pre_delete, sender=Media)
def delete_media(sender, instance, **kwargs):
    if instance.smb_video_id:
        a = delete_video(instance.smb_video_id)
        if instance.media_connection_type == "Info":
            delete_from_s3(instance, instance.id, "infos", "media")
        elif instance.media_connection_type == "TvShowTranslation":
            delete_from_s3(instance, instance.id, "tv_show_translations", "media")
