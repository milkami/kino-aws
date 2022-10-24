
from django.db import models
from django.utils.timezone import now

from cinemas.models import Cinemas


class Statistics(Cinemas):
    class Meta:
        proxy = True
        verbose_name = "Statistic"
        verbose_name_plural = "Statistics"

class AppUsers(models.Model):
    id = models.IntegerField(blank=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        managed = False
        db_table = "users"


class Errors(models.Model):
    error = models.TextField(null=True)
    alert = models.TextField(null=True)
    warning = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.pk 
    ## add to kino de parsers for bot erros manged = False!!
   