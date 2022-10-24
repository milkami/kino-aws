from django.contrib import admin
from .models import Admins

class AdminsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Admins._meta.get_fields()]

admin.site.register(Admins, AdminsAdmin)

# Register your models here.
