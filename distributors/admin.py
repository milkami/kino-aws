from secrets import token_hex

from django import forms
from django.contrib import admin

from .models import Distributors

# Register your models here.


class DistributorsForm(forms.ModelForm):

    locale = forms.CharField(disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["locale"].initial = "de"
        self.fields["hash_id"].initial = token_hex(20)

    class Meta:
        model = Distributors
        fields = "__all__"
        exclude = ["created_at", "updated_at"]


class DistributorsAdmin(admin.ModelAdmin):
    form = DistributorsForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "name",
        "hash_id",
    )
    search_fields = ("id", "name")


admin.site.register(Distributors, DistributorsAdmin)
