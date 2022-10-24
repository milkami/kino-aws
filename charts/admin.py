from datetime import date, datetime, timedelta

from django import forms
from django.contrib import admin
from django.template.defaultfilters import mark_safe

from .models import Charts

# from django.utils.timezone import now


# Register your models here.


class ChartsForm(forms.ModelForm):

    locale = forms.CharField(disabled=True)
    week_seats = forms.CharField(required=False)
    total_seats = forms.CharField(required=False)
    week_revenue = forms.CharField(required=True)
    total_revenue = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["locale"].initial = "de"
        self.fields["position"].label = mark_safe("<strong>Position</strong>")
        self.fields["previous"].label = mark_safe("<strong>Previous</strong>")
        self.fields["week_revenue"].label = mark_safe("<strong>Week revenue</strong>")
        self.fields["total_revenue"].label = mark_safe("<strong>Total revenue</strong>")

    class Meta:
        model = Charts
        fields = "__all__"
        exclude = ["created_at", "updated_at"]

    def clean_week_seats(self):
        if "." in self.cleaned_data["week_seats"]:
            self.cleaned_data["week_seats"] = self.cleaned_data["week_seats"].replace(
                ".", ""
            )
            return self.cleaned_data["week_seats"]
        if self.cleaned_data["week_seats"] == "":
            return
        else:
            return self.cleaned_data["week_seats"]

    def clean_total_seats(self):
        if "." in self.cleaned_data["total_seats"]:
            self.cleaned_data["total_seats"] = self.cleaned_data["total_seats"].replace(
                ".", ""
            )
            return self.cleaned_data["total_seats"]
        if self.cleaned_data["total_seats"] == "":
            return
        else:
            return self.cleaned_data["total_seats"]

    def clean_week_revenue(self):
        if "." in self.cleaned_data["week_revenue"]:
            self.cleaned_data["week_revenue"] = self.cleaned_data[
                "week_revenue"
            ].replace(".", "")
            return self.cleaned_data["week_revenue"]
        if self.cleaned_data["week_revenue"] == "":
            return
        else:
            return self.cleaned_data["week_revenue"]

    def clean_total_revenue(self):
        if "." in self.cleaned_data["total_revenue"]:
            self.cleaned_data["total_revenue"] = self.cleaned_data[
                "total_revenue"
            ].replace(".", "")
            return self.cleaned_data["total_revenue"]
        if self.cleaned_data["total_revenue"] == "":
            return
        else:
            return self.cleaned_data["total_revenue"]

    def save(self, commit=True):
        instance = super(ChartsForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance


@admin.action(description="Change Chart dates to current week")
def change_dates(modeladmin, request, queryset):
    today = date.today()
    start_date = today + timedelta(days=(1 - today.weekday()))
    if start_date > today:
        start_date = start_date - timedelta(days=7)
    current_week = start_date + timedelta(days=7)
    to_date = datetime(
        year=current_week.year, month=current_week.month, day=current_week.day, hour=17
    )
    from_date = datetime(
        year=start_date.year, month=start_date.month, day=start_date.day, hour=11
    )
    queryset.update(from_date=str(from_date), to_date=str(to_date))


class ChartsAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "info",
    ]
    form = ChartsForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "position",
        "previous",
        "movie_name",
        "week_revenue",
        "total_revenue",
        "from_date",
        "to_date",
    )
    actions = [change_dates]

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("position").select_related("info")

    def movie_name(self, obj):
        return mark_safe(
            f'<a href="/admin/movies/infos/{obj.info.id}/change">{obj.info.title}</a>'
        )

    movie_name.allow_tags = True  # type: ignore
    movie_name.short_description = "Info"  # type: ignore
    movie_name.admin_order_field = 'info__title'


admin.site.register(Charts, ChartsAdmin)
