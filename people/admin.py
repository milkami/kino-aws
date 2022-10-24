import re
from functools import reduce
from operator import or_

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.defaultfilters import mark_safe
from django.utils.html import format_html

from cms.aws_helpers import delete_people_from_s3, upload_people
from cms.tmdb_helpers import fetch_person_data

from .models import People

# Register your models here.


class PeopleForm(forms.ModelForm):
    photo_link = forms.CharField(required=False)
    lock_photo = forms.BooleanField(required=False)
    photo_file_upload = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locked_attributes = None
        if kwargs.get("instance"):
            locked_attributes = kwargs.get("instance").locked_attributes

        self.fields["photo_file_upload"].required = False
        self.fields["photo_file_upload"].label = mark_safe(
            "<strong>Upload photo</strong>"
        )
        self.fields["photo_link"].label = mark_safe("<strong>Photo link</strong>")
        self.fields["lock_photo"].label = "Lock"

        if locked_attributes:
            if "photo" in locked_attributes:
                self.fields["lock_photo"].initial = "on"

    class Meta:
        model = People
        fields = "__all__"


class PeopleAdmin(admin.ModelAdmin):
    form = PeopleForm
    
    change_form_template = "admin/person_change_form.html"
    list_display = (
        "id",
        "tmdb_id_link",
        "imdb_id_link",
        "name",
        "photo_tag",
        "also_known_as",
        "birthday",
        "deathday",
        "homepage_link",
        "place_of_birth",
        "popularity",
    )

    search_fields = ("name", "imdb_id", "tmdb_id", "id")

    fields = (
        "tmdb",
        "name",
        ("photo_tag", "lock_photo"),
        "photo_file_upload",
        "photo_link",
        "delete_photo",
        "also_known_as",
        "biography",
        "birthday",
        "deathday",
        "homepage",
        "place_of_birth",
        "popularity",
        "tmdb_id",
        "imdb_id",
        "show_images",
    )
    readonly_fields = (
        "tmdb",
        "photo_tag",
        "delete_photo",
    )
    list_per_page = 200

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("-popularity")

    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super(PeopleAdmin, self).get_search_results(
            request, queryset, search_term
        )
        search_words = re.split(",\s*", search_term)
        if search_words:
            q_objects = [
                Q(**{field + "__icontains": word})
                for field in self.search_fields
                for word in search_words
            ]
            queryset = queryset.filter(reduce(or_, q_objects))
        return queryset, use_distinct

    def tmdb_id_link(self, obj):
        return format_html(
            '<a href="https://www.themoviedb.org/person/%s">%s</a>'
            % (obj.tmdb_id, obj.tmdb_id)
        )

    tmdb_id_link.allow_tags = True  # type: ignore
    tmdb_id_link.short_description = "tmdb id"  # type: ignore

    def imdb_id_link(self, obj):
        return format_html(
            '<a href="http://www.imdb.com/name/%s">%s</a>' % (obj.imdb_id, obj.imdb_id)
        )

    imdb_id_link.allow_tags = True  # type: ignore
    imdb_id_link.short_description = "imdb id"  # type: ignore

    def homepage_link(self, obj):
        return format_html("<a href=%s>%s</a>" % (obj.homepage, obj.homepage))

    homepage_link.allow_tags = True  # type: ignore
    homepage_link.short_description = "homepage"  # type: ignore

    def tmdb(self, obj):
        return format_html(
            '<input type="submit" value=" Fetch Data from TMDB " ' 'name="fetching">'
        )

    tmdb.allow_tags = True  # type: ignore

    def delete_photo(self, obj):
        return format_html(
            '<input type="submit" value="Delete Photo" name="delete_photo">'
        )

    delete_photo.allow_tags = True  # type: ignore

    def response_change(self, request, obj):

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_photo = request.POST.get("lock_photo")
        locked_attributes = None

        if lock_photo == "on":
            locked_attributes = "---"
            if lock_photo == "on":
                locked_attributes += "\r\n- photo"

        obj.locked_attributes = locked_attributes
        obj.save()

        # __________________________________________________________
        if "photo_file_upload" in request.FILES:
            obj.photo_file_name = request.FILES["photo_file_upload"]
            obj.save()
            upload_people(obj, request.FILES["photo_file_upload"], obj.id, "people")

        if obj.photo_file_name == "":
            obj.photo_file_name = None
            obj.save()

        if "fetching" in request.POST:
            message = "Nothing was done."
            message = fetch_person_data(obj, obj.id, obj.tmdb_id)
            self.message_user(request, message)
            return HttpResponseRedirect(".")
        elif "delete_photo" in request.POST:
            obj.paths_to_photos = None
            obj.photo_file_name = None
            obj.photo_path = None
            obj.save()
            delete_people_from_s3(obj, obj.id, "people")
            return HttpResponseRedirect(".")
        else:
            photo_url = request.POST.get("photo_link")

            if photo_url:
                paths_to_photos = "---"
                paths_to_photos += "\r\n- " + photo_url
                obj.paths_to_photos = paths_to_photos
                obj.photo_path = photo_url
                obj.photo_file_name = photo_url
                obj.save()
                upload_people(obj, photo_url, obj.id, "people")

            return super(PeopleAdmin, self).response_change(request, obj)


class UserAdmin(BaseUserAdmin):
    add_form_template = "admin/add_user_form.html"
    change_form_template = "admin/change_user_form.html"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(People, PeopleAdmin)
