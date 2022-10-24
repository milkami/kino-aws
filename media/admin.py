import re
import secrets

from django import forms
from django.contrib import admin
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from cms.aws_helpers import upload
from cms.trailer_helpers import delete_video, get_video, set_video, update_video
from movies.models import Infos, Movies
from tvshows.models import Seasons, TvShows, TvShowTranslations

from .models import Media

# Register your models here.


class MediaForm(forms.ModelForm):

    media_connection_type = forms.CharField(disabled=False)
    photo_link = forms.CharField(required=False)
    photo_file_upload = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        media_connection_id = None

        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "media_connection_id" in path:
                media_connection_id = re.findall("media_connection_id=\d+", path)
                if media_connection_id:
                    media_connection_id = media_connection_id[0]
                    media_connection_id = re.findall("\d+", media_connection_id)[0]
            elif "%3D" in path:
                media_connection_id = path.split("%3D")[-1]

        self.fields["media_connection_id"].initial = media_connection_id
        self.fields["media_connection_type"].initial = "Info"

        self.fields["photo_link"].label = mark_safe("<strong>Photo link</strong>")
        self.fields["media_connection_id"].label = mark_safe(
            "<strong>Media connection id</strong>"
        )
        self.fields["name"].label = mark_safe("<strong>Name</strong>")
        self.fields["popularity"].label = mark_safe("<strong>Popularity</strong>")

        self.fields["featured"].label = mark_safe("<strong>Featured</strong>")

        self.fields["photo_file_upload"].required = False
        self.fields["photo_file_upload"].label = mark_safe(
            "<strong>Upload photo</strong>"
        )

    class Meta:
        model = Media
        fields = "__all__"
        exclude = [
            "created_at",
            "updated_at",
            "photo_content_type",
            "photo_file_size",
            "photo_updated_at",
        ]


class PhotoFilter(admin.SimpleListFilter):
    title = "Photo status"
    parameter_name = "photo"

    def lookups(self, request, model_admin):
        return (
            ("1", "Media with Photo"),
            ("0", "Media without Photo"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(
                ~Q(photo_file_name="") & Q(photo_file_name__isnull=False)
            )
        elif self.value() == "0":
            return queryset.filter(
                Q(photo_file_name="") | Q(photo_file_name__isnull=True)
            )
        else:
            return queryset


class TypeFilter(admin.SimpleListFilter):
    title = "Type"
    parameter_name = "media_connection_type"

    def lookups(self, request, model_admin):
        return (
            ("1", "Movies Media"),
            ("0", "Tv Shows Media"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(media_connection_type__in=["Info", "Movie"])
        elif self.value() == "0":
            return queryset.filter(
                media_connection_type__in=["TvShow", "TvShowTranslation"]
            )
        else:
            return queryset


class ActiveMediaFilter(admin.SimpleListFilter):
    title = "Active status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            (1, "Active"),
            (0, "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(active=self.value())
        else:
            return queryset


class MediaAdmin(admin.ModelAdmin):
    form = MediaForm
    
    change_form_template = "upload_video_change_form.html"
    list_display = (
        "id",
        "photo",
        "media_name",
        "duration",
        "smb_video_id_link",
        "active",
        "trailer_link",
        "created_at",
        "popularity",
    )
    list_filter = (PhotoFilter, TypeFilter, ActiveMediaFilter)
    search_fields = ("name",)
    readonly_fields = ("id", "smb_video_id_link", "active", "smb_duration")

    fields = (
        "id",
        "media_connection_type",
        "media_connection_id",
        "active",
        "name",
        "smb_video_id",
        "smb_video_id_link",
        "photo_file_upload",
        "photo_link",
        "trailer_language",
        "popularity",
        "featured",
        "smb_duration",
        "smb_checked_at",
    )
    def get_queryset(self, request):
        return super().get_queryset(request).extra(
            select={
                "movie_name":"SELECT name FROM movies WHERE id=media.media_connection_id",
                "info_movie_name":"SELECT name FROM movies WHERE id IN (SELECT movie_id FROM infos WHERE id=media.media_connection_id)",
                "info_movie_id":"SELECT movie_id FROM infos WHERE id=media.media_connection_id",
                "tv_show_name":"SELECT name FROM tv_shows WHERE id=media.media_connection_id",
                "tv_show_translation_tv_show_name":"SELECT name FROM tv_shows WHERE id IN (SELECT tv_show_id FROM tv_show_translations WHERE id=media.media_connection_id)",
                "tv_show_translation_tv_show_id":"SELECT tv_show_id FROM tv_show_translations WHERE id=media.media_connection_id",
                "season_tv_show_name":"SELECT name FROM tv_shows WHERE id IN (SELECT tv_show_id FROM seasons WHERE id=media.media_connection_id)",
                "season_tv_show_id":"SELECT tv_show_id FROM seasons WHERE id=media.media_connection_id"
                }
        )

    def trailer_link(self, obj):
        if obj.trailer_url != None:
            return mark_safe(f"<a href={obj.trailer_url}>{obj.trailer_url}</a>")
        else:
            return "-"

    trailer_link.short_description = "trailer URL"  # type: ignore

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(MediaAdmin, self).get_search_results(
            request, queryset, search_term
        )

        if search_term == "":
            return queryset, False

        elif search_term.isdecimal():
            queryset_media = queryset.filter(id=search_term)
            movie_ids = Movies.objects.filter(tmdb_id=search_term).values("id")
            info_ids = Infos.objects.filter(movie__tmdb_id=search_term).values("id")
            tvshows_ids = TvShows.objects.filter(tmdb_id=search_term).values("id")
            tvshowtranslations_ids = TvShowTranslations.objects.filter(
                tv_show__tmdb_id=search_term
            ).values("id")
            queryset_movies = Media.objects.filter(
                media_connection_type="Movie"
            ).filter(media_connection_id__in=movie_ids)
            queryset_infos = Media.objects.filter(media_connection_type="Info").filter(
                media_connection_id__in=info_ids
            )
            queryset_tvshows = Media.objects.filter(
                media_connection_type="TvShow"
            ).filter(media_connection_id__in=tvshows_ids)
            queryset_tvstranslations = Media.objects.filter(
                media_connection_type="TvShowTranslation"
            ).filter(media_connection_id__in=tvshowtranslations_ids)
            queryset = (
                queryset_media
                | queryset_tvshows
                | queryset_movies
                | queryset_infos
                | queryset_tvstranslations
            )
            return queryset, True

        elif search_term[2:].isdecimal():
            movie_ids = Movies.objects.filter(imdb_id=search_term).values("id")
            info_ids = Infos.objects.filter(movie__imdb_id=search_term).values("id")
            tvshows_ids = TvShows.objects.filter(imdb_id=search_term).values("id")
            tvshowtranslations_ids = TvShowTranslations.objects.filter(
                tv_show__imdb_id=search_term
            ).values("id")
            queryset_movies = Media.objects.filter(
                media_connection_type="Movie"
            ).filter(media_connection_id__in=movie_ids)
            queryset_infos = Media.objects.filter(media_connection_type="Info").filter(
                media_connection_id__in=info_ids
            )
            queryset_tvshows = Media.objects.filter(
                media_connection_type="TvShow"
            ).filter(media_connection_id__in=tvshows_ids)
            queryset_tvstranslations = Media.objects.filter(
                media_connection_type="TvShowTranslation"
            ).filter(media_connection_id__in=tvshowtranslations_ids)
            queryset = (
                queryset_tvshows
                | queryset_movies
                | queryset_infos
                | queryset_tvstranslations
            )
            return queryset, True
        else:
            queryset_media = queryset.filter(name__icontains=search_term)
            movie_ids = Movies.objects.filter(
                original_title__icontains=search_term
            ).values("id")
            info_ids = Infos.objects.filter(title__icontains=search_term).values("id")
            tvshows_ids = TvShows.objects.filter(
                original_title__icontains=search_term
            ).values("id")
            tvshowtranslations_ids = TvShowTranslations.objects.filter(
                title__icontains=search_term
            ).values("id")
            queryset_movies = Media.objects.filter(
                media_connection_type="Movie"
            ).filter(media_connection_id__in=movie_ids)
            queryset_infos = Media.objects.filter(media_connection_type="Info").filter(
                media_connection_id__in=info_ids
            )
            queryset_tvshows = Media.objects.filter(
                media_connection_type="TvShow"
            ).filter(media_connection_id__in=tvshows_ids)
            queryset_tvstranslations = Media.objects.filter(
                media_connection_type="TvShowTranslation"
            ).filter(media_connection_id__in=tvshowtranslations_ids)
            queryset = (
                queryset_media
                | queryset_infos
                | queryset_tvshows
                | queryset_movies
                | queryset_tvstranslations
            )
            return queryset, True

    def media_name(self, obj):
        if obj.media_connection_type == "Info":
            return mark_safe(
                "<a href='/admin/movies/movies/%s/change/'>%s</a>"
                % (obj.info_movie_id, obj.info_movie_name)
            )
        elif obj.media_connection_type == "Movie":
            return mark_safe(
                "<a href='/admin/movies/movies/%s/change/'>%s</a>"
                % (obj.media_connection_id, obj.movie_name)
            )
        elif obj.media_connection_type == "TvShow":
            return mark_safe(
                "<a href='/admin/tvshows/tvshows/%s/change/'>%s</a>"
                % (obj.media_connection_id, obj.tv_show_name)
            )
        elif obj.media_connection_type == "Season":
            return mark_safe(
                "<a href='/admin/tvshows/tvshows/%s/change/'>%s</a>"
                % (obj.season_tv_show_id, obj.season_tv_show_name)
            )
        elif obj.media_connection_type == "TvShowTranslation":
            return format_html(
                "<a href='/admin/tvshows/tvshows/%s/change/'>%s</a>"
                % (obj.tv_show_translation_tv_show_id, obj.tv_show_translation_tv_show_name)
            )

    media_name.short_description = "title"  # type: ignore
    media_name.allow_tags = True  # type: ignore

    def duration(self, obj):
        if obj.smb_duration:
            m, s = divmod(obj.smb_duration, 60)
            if m < 10:
                m = "0" + str(m)
            if s < 10:
                s = "0" + str(s)
            return format_html("<p> %s:%s </p>" % (m, s))
        else:
            return format_html("<p>%s</p>" % (obj.smb_duration))

    duration.short_description = "duration"  # type: ignore
    duration.allow_tags = True  # type: ignore

    def photo(self, obj):
        if obj.photo_file_name:
            if obj.media_connection_type in ["TvShow", "Info", "Movie", "Season"]:
                return format_html(
                    '<img src="{}?{}"'
                    'style="width: 190px;height:90px; object-fit: cover;"/>'.format(
                        f"https://s3-eu-west-1.amazonaws.com/kinode/production/"
                        f"{obj.media_connection_type.lower()}s/media/{obj.id}/tiny.jpg",
                        secrets.randbelow(100000),
                    )
                )

            elif obj.media_connection_type == "TvShowTranslation":
                return format_html(
                    '<img src="{}?{}"'
                    'style="width: 190px;height:90px; object-fit: cover;"/>'.format(
                        f"https://s3-eu-west-1.amazonaws.com/kinode/production/"
                        f"tv_show_translations/media/{obj.id}/tiny.jpg",
                        secrets.randbelow(100000),
                    )
                )
        else:
            return "-"

    photo.short_description = "Photo"  # type: ignore
    photo.allow_tags = True  # type: ignore

    def smb_video_id_link(self, obj):
        return format_html(
            '<a href="%s">%s</a>'
            % (
                f"http://videos.kntk.de/files/{obj.smb_video_id}",
                f"http://videos.kntk.de/files/{obj.smb_video_id}",
            )
        )

    smb_video_id_link.short_description = "smb video url"  # type: ignore
    smb_video_id_link.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        smb_video = get_video(obj.smb_video_id)

        if smb_video:
            obj.smb_duration = smb_video["duration"]
            obj.active = True
        obj.save()

        if "photo_file_upload" in request.FILES:
            obj.photo_file_name = request.FILES["photo_file_upload"]
            obj.save()

            if obj.media_connection_type == "Info":
                upload(
                    obj, request.FILES["photo_file_upload"], obj.id, "infos", "media"
                )
            elif obj.media_connection_type == "TvShowTranslation":
                upload(
                    obj,
                    request.FILES["photo_file_upload"],
                    obj.id,
                    "tv_show_translations",
                    "media",
                )

        if obj.photo_file_name == "":
            obj.photo_file_name = None
            obj.save()

        photo_url = request.POST.get("photo_link")
        if photo_url:
            if obj.media_connection_type == "Info":
                upload(obj, photo_url, obj.id, "infos", "media")
                obj.photo_file_name = photo_url
            elif obj.media_connection_type == "TvShowTranslation":
                upload(obj, photo_url, obj.id, "tv_show_translations", "media")
                obj.photo_file_name = photo_url

        preview_image = None
        if obj.media_connection_type == "Info":
            if obj.photo_file_name != None:
                preview_image = (
                    f"https://s3-eu-west-1.amazonaws.com/kinode/production/infos/media/{obj.id}/original.jpg?"
                    + str(secrets.randbelow(100000))
                )
            info = Infos.objects.filter(id=obj.media_connection_id).first()
            if not "Trailer deutsch" in obj.name:
                obj.name = info.title + " | Trailer deutsch"
                obj.save()
            update_video(obj.smb_video_id, obj, None, preview_image)

        elif obj.media_connection_type == "TvShowTranslation":
            if obj.photo_file_name != None:
                preview_image = (
                    f"https://s3-eu-west-1.amazonaws.com/kinode/production/tv_show_translations/media/{obj.id}/original.jpg?"
                    + str(secrets.randbelow(100000))
                )
            tv_show_translation = TvShowTranslations.objects.filter(
                id=obj.media_connection_id
            ).first()
            if not "Trailer deutsch" in obj.name:
                obj.name = tv_show_translation.title + " | Trailer deutsch"
                obj.save()
            update_video(obj.smb_video_id, obj, None, preview_image)

        return super(MediaAdmin, self).response_change(request, obj)


admin.site.register(Media, MediaAdmin)
