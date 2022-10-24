# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils.timezone import now


class Distributors(models.Model):
    id = models.AutoField(primary_key=True)
    hash_id = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now, editable=True)
    updated_at = models.DateTimeField(default=now, editable=True)

    class Meta:
        managed = False
        db_table = "distributors"
        verbose_name = "Distributor"
        verbose_name_plural = "Distributors"

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ""
