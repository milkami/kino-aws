from datetime import datetime

import pytz
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.defaultfilters import mark_safe
from django.utils.html import format_html

from cms.aws_helpers import (
    delete_spotlight_from_s3,
    delete_spotlights_from_s3,
    upload_spotlights,
)

from .models import Spotlights

# Register your models here.

utc = pytz.UTC


class SpotlightsForm(forms.ModelForm):

    background_56_portrait_link = forms.CharField(required=False)
    background_75_portrait_link = forms.CharField(required=False)
    background_75_landscape_link = forms.CharField(required=False)
    featured_image_link = forms.CharField(required=False)
    background_56_portrait_upload = forms.FileField()
    background_75_portrait_upload = forms.FileField()
    background_75_landscape_upload = forms.FileField()
    featured_image_upload = forms.FileField()
    video_56_portrait_upload = forms.FileField()

    def __init__(self, *args, **kwargs):
        spotlight_type = None
        location = None
        super().__init__(*args, **kwargs)
        self.fields["spotlight_type"].choices = (
            ("coming_soon", "coming_soon"),
            ("in_cinemas", "in_cinemas"),
            ("on_demand", "on_demand"),
            ("tv_shows", "tv_shows"),
            ("movie_trailer", "movie_trailer"),
            ("tv_show_trailer", "tv_show_trailer"),
            ("list", "list"),
            ("person", "person"),
            ("ad", "ad"),
            ("", ""),
        )
        self.fields["subtitle"].required = False

        self.fields["location"].choices = (
            ("home_tab", "home_tab"),
            ("in_cinemas_tab", "in_cinemas_tab"),
            ("coming_soon_tab", "coming_soon_tab"),
            ("on_demand_tab", "on_demand_tab"),
            ("tv_shows_tab", "tv_shows_tab"),
            ("", ""),
        )

        if kwargs.get("instance"):
            instance = kwargs["instance"]
            spotlight_type = instance.spotlight_type
            location = instance.location

        self.fields["background_56_portrait_upload"].required = False

        self.fields["background_56_portrait_upload"].label = mark_safe(
            "<strong>Background 56 portrait file upload</strong>"
        )
        self.fields["background_75_portrait_upload"].required = False

        self.fields["background_75_portrait_upload"].label = mark_safe(
            "<strong>Background 75 portrait file upload</strong>"
        )
        self.fields["background_75_landscape_upload"].required = False

        self.fields["background_75_landscape_upload"].label = mark_safe(
            "<strong>Background 75 landscape file upload</strong>"
        )
        self.fields["featured_image_upload"].required = False

        self.fields["featured_image_upload"].label = mark_safe("Featured image upload")
        self.fields["video_56_portrait_upload"].required = False

        self.fields["background_56_portrait_link"].label = mark_safe(
            "<strong>Background 56 portrait link</strong>"
        )
        self.fields["background_75_portrait_link"].label = mark_safe(
            "<strong>Background 75 portrait link</strong>"
        )
        self.fields["background_75_landscape_link"].label = mark_safe(
            "<strong>Background 75 landscape link</strong>"
        )
        self.fields["featured_image_link"].label = mark_safe("Featured image link")
        # ______________________________________________________________

        self.fields["spotlight_type"].initial = spotlight_type if spotlight_type else ""
        self.fields["location"].initial = location if location else "home_tab"

    class Meta:
        model = Spotlights
        fields = "__all__"
        exclude = [
            "background_56_portrait_content_type",
            "background_75_portrait_content_type",
            "background_75_landscape_content_type",
            "background_56_portrait_file_size",
            "background_56_portrait_updated_at",
            "background_75_landscape_file_size",
            "background_75_landscape_updated_at",
            "background_75_portrait_file_size",
            "background_75_portrait_updated_at",
            "video_56_portrait_content_type",
            "video_56_portrait_file_size",
            "video_56_portrait_updated_at",
            "created_at",
            "updated_at",
            "photo_content_type",
            "photo_file_size",
            "photo_updated_at",
            "photo_file_name",
        ]


class ActiveFilter(admin.SimpleListFilter):
    title = "Active status"
    parameter_name = "available_until"

    def lookups(self, request, model_admin):
        return (
            ("all", "All"),
            (None, "Active"),
            ("False", "Expired"),
            ("future", "Scheduled"),
            ("featured", "Featured"),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": cl.get_query_string(
                    {
                        self.parameter_name: lookup,
                    },
                    [],
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() == "future":
            return queryset.filter(available_from__gt=utc.localize(datetime.now()))
        elif self.value() == "False":
            return queryset.filter(available_until__lt=utc.localize(datetime.now()))
        elif self.value() == None:
            return queryset.filter(
                available_until__gt=utc.localize(datetime.now())
            ).exclude(available_from__gt=utc.localize(datetime.now()))
        elif self.value() == "featured":
            return queryset.exclude(location="home_tab")
        elif self.value() == "all":
            return queryset


class LocationsFilter(admin.SimpleListFilter):
    title = "Location"
    parameter_name = "location"

    def lookups(self, request, model_admin):
        return (
            ("home_tab", "home_tab"),
            ("in_cinemas_tab", "in_cinemas_tab"),
            ("coming_soon_tab", "coming_soon_tab"),
            ("on_demand_tab", "on_demand_tab"),
            ("tv_shows_tab", "tv_shows_tab"),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(location=self.value())


class SpotlightTypeFilter(admin.SimpleListFilter):
    title = "Spotlight type"
    parameter_name = "spotlight_type"

    def lookups(self, request, model_admin):
        return (
            ("coming_soon", "coming_soon"),
            ("in_cinemas", "in_cinemas"),
            ("on_demand", "on_demand"),
            ("tv_shows", "tv_shows"),
            ("movie_trailer", "movie_trailer"),
            ("tv_show_trailer", "tv_show_trailer"),
            ("list", "list"),
            ("person", "person"),
            ("ad", "ad"),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(spotlight_type=self.value())


class SpotlightsAdmin(admin.ModelAdmin):
    ordering = ["position"]
    form = SpotlightsForm
    change_form_template = "admin/spotlight_change_form.html"
    save_on_top = True
    list_display = (
        "id",
        "position",
        "title_subtitle",
        "pic_56p",
        "pic_75p",
        "pic_75l",
        "spotlight_type",
        "available_dates_list_field",
        "target_id",
    )
    list_filter = (ActiveFilter, SpotlightTypeFilter, LocationsFilter)
    readonly_fields = (
        "id",
        "delete_background_56_portrait",
        "delete_background_75_portrait",
        "delete_background_75_landscape",
        "delete_video_56_portrait",
        "delete_featured_image",
    )

    fields = (
        "id",
        "location",
        "spotlight_type",
        "target_id",
        "target_link",
        "position",
        "available_from",
        "available_until",
        "title",
        "subtitle",
        "background_56_portrait_upload",
        "background_56_portrait_link",
        "delete_background_56_portrait",
        "video_56_portrait_upload",
        "delete_video_56_portrait",
        "background_75_portrait_upload",
        "background_75_portrait_link",
        "delete_background_75_portrait",
        "background_75_landscape_upload",
        "background_75_landscape_link",
        "delete_background_75_landscape",
        "featured_image_upload",
        "featured_image_link",
        "delete_featured_image",
    )

    def get_list_display(self, request):
        if request.GET.get("available_until") == "featured":
            return (
                "id",
                "position",
                "title_subtitle",
                "pic_56p",
                "pic_75p",
                "pic_75l",
                "featured_image",
                "spotlight_type",
                "available_dates_list_field",
                "target_id",
            )
        elif request.GET.get("available_until") == None:
            if Spotlights.objects.exclude(location="home_tab").count() > 0:
                return (
                    "id",
                    "position",
                    "title_subtitle",
                    "pic_56p",
                    "pic_75p",
                    "pic_75l",
                    "featured_image",
                    "spotlight_type",
                    "available_dates_list_field",
                    "target_id",
                )
            else:
                return self.list_display
        else:
            return self.list_display

    def title_subtitle(self, obj):
        if obj.spotlight_type in ["coming_soon", "in_cinemas", "movie_trailer", "on_demand"]:
            href_value = f" href='/admin/movies/infos/{obj.target_id}'"
        elif obj.spotlight_type in ["tv_shows", "tv_show_trailer"]:
            href_value = f" href='/admin/tvshows/tvshowtranslations/{obj.target_id}'"
        else:
            href_value = ""

        content = f"<b>{obj.title}</b><br>{obj.subtitle if obj.subtitle else ''}"
        value = f"<a{href_value}>{content}</a>" if href_value else content

        return mark_safe(value)

    title_subtitle.admin_order_field = "title"  # type: ignore
    title_subtitle.short_description = "Title"  # type: ignore

    def available_dates_list_field(self, obj):
        return mark_safe(
            f"<b>From:</b><br><div style='width:80px'>{obj.available_from.strftime('%d %b %Y %H:%M')}</div><br><br><b>Until:</b><br>{obj.available_until.strftime('%d %b %Y %H:%M')}"
        )

    available_dates_list_field.short_description = "Available"  # type: ignore

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            delete_spotlight_from_s3(obj.id, "spotlights")

        queryset.delete()

    def pic_56p(self, obj):
        if obj.background_56_portrait_file_name:
            return format_html(
                '<a href="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/background_56_portraits/large.jpg">'
                '<img src="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/background_56_portraits/small.jpg" style="height: 150px;"/>'
                "</a>" % (obj.id, obj.id)
            )
        else:
            return "No image"

    pic_56p.allow_tags = True  # type: ignore
    pic_56p.short_description = "56p"  # type: ignore

    def pic_75p(self, obj):
        if obj.background_75_portrait_file_name:
            return format_html(
                '<a href="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/background_75_portraits/large.jpg">'
                '<img src="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/background_75_portraits/small.jpg" style="height: 150px;"/>'
                "</a>" % (obj.id, obj.id)
            )
        else:
            return "No image"

    pic_75p.allow_tags = True  # type: ignore
    pic_75p.short_description = "75p"  # type: ignore

    def pic_75l(self, obj):
        if obj.background_75_landscape_file_name:
            return format_html(
                '<a href="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/background_75_landscapes/large.jpg">'
                '<img src="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/background_75_landscapes/small.jpg" style="height: 150px;"/>'
                "</a>" % (obj.id, obj.id)
            )
        else:
            return "No image"

    pic_75l.allow_tags = True  # type: ignore
    pic_75l.short_description = "75l"  # type: ignore

    def featured_image(self, obj):
        if obj.photo_file_name:
            return format_html(
                '<a href="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/photos/large.jpg">'
                '<img src="https://s3-eu-west-1.amazonaws.com/kinode/production/spotlights/%s/photos/small.jpg" style="height: 150px;"/>'
                "</a>" % (obj.id, obj.id)
            )
        else:
            return "No image"

    featured_image.allow_tags = True  # type: ignore
    featured_image.short_description = "Photo"  # type: ignore

    def delete_background_56_portrait(self, obj):
        return format_html(
            '<input type="submit" value="Delete background 56 portrait" name="delete_background_56_portrait">'
        )

    delete_background_56_portrait.allow_tags = True  # type: ignore

    def delete_background_75_portrait(self, obj):
        return format_html(
            '<input type="submit" value="Delete background 75 portrait" name="delete_background_75_portrait">'
        )

    delete_background_75_portrait.allow_tags = True  # type: ignore

    def delete_background_75_landscape(self, obj):
        return format_html(
            '<input type="submit" value="Delete background 75 landscape" name="delete_background_75_landscape">'
        )

    delete_background_75_landscape.allow_tags = True  # type: ignore

    def delete_featured_image(self, obj):
        return format_html(
            '<input type="submit" value="Delete featured image" name="delete_featured_image">'
        )

    delete_featured_image.allow_tags = True  # type: ignore

    def delete_video_56_portrait(self, obj):
        return format_html(
            '<input type="submit" value="Delete video 56 portrait" name="delete_video_56_portrait">'
        )

    delete_video_56_portrait.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        background_56_portrait_url = request.POST.get("background_56_portrait_link")
        background_75_portrait_url = request.POST.get("background_75_portrait_link")
        background_75_landscape_url = request.POST.get("background_75_landscape_link")
        featured_image_url = request.POST.get("featured_image_link")

        if background_56_portrait_url:
            obj.background_56_portrait_file_name = background_56_portrait_url
            obj.save()
            upload_spotlights(
                obj, background_56_portrait_url, "spotlights", "background_56_portraits"
            )
        if background_75_portrait_url:
            obj.background_75_portrait_file_name = background_75_portrait_url
            obj.save()
            upload_spotlights(
                obj, background_75_portrait_url, "spotlights", "background_75_portraits"
            )
        if background_75_landscape_url:
            obj.background_75_landscape_file_name = background_75_landscape_url
            obj.save()
            upload_spotlights(
                obj,
                background_75_landscape_url,
                "spotlights",
                "background_75_landscapes",
            )
        if featured_image_url:
            obj.photo_file_name = featured_image_url
            obj.save()
            upload_spotlights(obj, background_75_portrait_url, "spotlights", "photos")

        if "background_56_portrait_upload" in request.FILES:
            obj.background_56_portrait_file_name = request.FILES[
                "background_56_portrait_upload"
            ]
            obj.save()
            upload_spotlights(
                obj,
                request.FILES["background_56_portrait_upload"],
                "spotlights",
                "background_56_portraits",
            )

        if obj.background_56_portrait_file_name == "":
            obj.background_56_portrait_file_name = None
            obj.save()

        if "background_75_portrait_upload" in request.FILES:
            obj.background_75_portrait_file_name = request.FILES[
                "background_75_portrait_upload"
            ]
            obj.save()
            upload_spotlights(
                obj,
                request.FILES["background_75_portrait_upload"],
                "spotlights",
                "background_75_portraits",
            )

        if obj.background_75_portrait_file_name == "":
            obj.background_75_portrait_file_name = None
            obj.save()

        if "background_75_landscape_upload" in request.FILES:
            obj.background_75_landscape_file_name = request.FILES[
                "background_75_landscape_upload"
            ]
            obj.save()
            upload_spotlights(
                obj,
                request.FILES["background_75_landscape_upload"],
                "spotlights",
                "background_75_landscapes",
            )

        if obj.background_75_landscape_file_name == "":
            obj.background_75_landscape_file_name = None
            obj.save()

        if "featured_image_upload" in request.FILES:
            obj.photo_file_name = request.FILES["featured_image_upload"]
            obj.save()
            upload_spotlights(
                obj, request.FILES["featured_image_upload"], "spotlights", "photos"
            )

        if obj.photo_file_name == "":
            obj.photo_file_name = None
            obj.save()

        if "video_56_portrait_upload" in request.FILES:
            obj.video_56_portrait_file_name = request.FILES["video_56_portrait_upload"]
            obj.save()
            upload_spotlights(
                obj,
                request.FILES["video_56_portrait_upload"],
                "spotlights",
                "video_56_portraits",
            )

        if obj.video_56_portrait_file_name == "":
            obj.video_56_portrait_file_name = None
            obj.save()

        if "delete_background_56_portrait" in request.POST:
            obj.background_56_portrait_file_name = None
            obj.save()
            delete_spotlights_from_s3(
                obj, obj.id, "spotlights", "background_56_portraits"
            )
            return HttpResponseRedirect(".")
        elif "delete_background_75_portrait" in request.POST:
            obj.background_75_portrait_file_name = None
            obj.save()
            delete_spotlights_from_s3(
                obj, obj.id, "spotlights", "background_75_portraits"
            )
            return HttpResponseRedirect(".")
        elif "delete_background_75_landscape" in request.POST:
            obj.background_75_landscape_file_name = None
            obj.save()
            delete_spotlights_from_s3(
                obj, obj.id, "spotlights", "background_75_landscapes"
            )
            return HttpResponseRedirect(".")
        elif "delete_video_56_portrait" in request.POST:
            obj.video_56_portrait_file_name = None
            obj.save()
            delete_spotlights_from_s3(obj, obj.id, "spotlights", "video_56_portraits")
            return HttpResponseRedirect(".")
        elif "delete_featured_image" in request.POST:
            obj.photo_file_name = None
            obj.save()
            delete_spotlights_from_s3(obj, obj.id, "spotlights", "photos")
            return HttpResponseRedirect(".")
        else:
            return super(SpotlightsAdmin, self).response_change(request, obj)
        
    def save_model(self, request, obj, form, change):
        if not change:
            background_56_portrait_url = request.POST.get("background_56_portrait_link")
            background_75_portrait_url = request.POST.get("background_75_portrait_link")
            background_75_landscape_url = request.POST.get("background_75_landscape_link")
            featured_image_url = request.POST.get("featured_image_link")

            if background_56_portrait_url:
                obj.background_56_portrait_file_name = background_56_portrait_url
                obj.save()
                upload_spotlights(
                    obj, background_56_portrait_url, "spotlights", "background_56_portraits"
                )
            if background_75_portrait_url:
                obj.background_75_portrait_file_name = background_75_portrait_url
                obj.save()
                upload_spotlights(
                    obj, background_75_portrait_url, "spotlights", "background_75_portraits"
                )
            if background_75_landscape_url:
                obj.background_75_landscape_file_name = background_75_landscape_url
                obj.save()
                upload_spotlights(
                    obj,
                    background_75_landscape_url,
                    "spotlights",
                    "background_75_landscapes",
                )
            if featured_image_url:
                obj.photo_file_name = featured_image_url
                obj.save()
                upload_spotlights(obj, background_75_portrait_url, "spotlights", "photos")

            if "background_56_portrait_upload" in request.FILES:
                obj.background_56_portrait_file_name = request.FILES[
                    "background_56_portrait_upload"
                ]
                obj.save()
                upload_spotlights(
                    obj,
                    request.FILES["background_56_portrait_upload"],
                    "spotlights",
                    "background_56_portraits",
                )
            if "background_75_portrait_upload" in request.FILES:
                obj.background_75_portrait_file_name = request.FILES[
                    "background_75_portrait_upload"
                ]
                obj.save()
                upload_spotlights(
                    obj,
                    request.FILES["background_75_portrait_upload"],
                    "spotlights",
                    "background_75_portraits",
                )
            if "background_75_landscape_upload" in request.FILES:
                obj.background_75_landscape_file_name = request.FILES[
                    "background_75_landscape_upload"
                ]
                obj.save()
                upload_spotlights(
                    obj,
                    request.FILES["background_75_landscape_upload"],
                    "spotlights",
                    "background_75_landscapes",
                )
            if "featured_image_upload" in request.FILES:
                obj.photo_file_name = request.FILES["featured_image_upload"]
                obj.save()
                upload_spotlights(
                    obj, request.FILES["featured_image_upload"], "spotlights", "photos"
                )
            if "video_56_portrait_upload" in request.FILES:
                obj.video_56_portrait_file_name = request.FILES["video_56_portrait_upload"]
                obj.save()
                upload_spotlights(
                    obj,
                    request.FILES["video_56_portrait_upload"],
                    "spotlights",
                    "video_56_portraits",
                )
        super().save_model(request, obj, form, change)


admin.site.register(Spotlights, SpotlightsAdmin)
