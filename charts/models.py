# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from datetime import timedelta

import pytz
from django.db import models
from django.utils.timezone import now

from movies.models import Infos

utc = pytz.UTC
current_week = now() + timedelta(days=7)


class Charts(models.Model):
    id = models.AutoField(primary_key=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    info = models.ForeignKey(
        Infos, on_delete=models.CASCADE, db_column="info_id", related_name="chains"
    )
    position = models.IntegerField()
    previous = models.IntegerField(blank=True, null=True)
    week_seats = models.IntegerField(blank=True, null=True)
    total_seats = models.IntegerField(blank=True, null=True)
    week_revenue = models.IntegerField()
    total_revenue = models.IntegerField()
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)
    from_date = models.DateTimeField(default=now, editable=True)
    to_date = models.DateTimeField(default=current_week, editable=True)

    def __str__(self):
        if self.info.title:
            return self.info.title
        else:
            return ""

    class Meta:
        managed = False
        db_table = "charts"
        verbose_name = "Chart"
        verbose_name_plural = "Charts"

    def save(self, *args, **kwargs):
        # value = self.value # self.value is a model field.
        super().save(*args, **kwargs)
