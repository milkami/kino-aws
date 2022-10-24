import json
import re
from datetime import datetime, timedelta
from functools import reduce
from itertools import chain
from operator import or_

import pytz
import requests
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.db.models import Q, Count, F
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.utils.html import format_html, mark_safe

from media.models import Media
from movies.models import Infos, Movies, MoviesPeople
# from other.models import SettingGroups

from .models import (
    Chains,
    Cinemas,
    MoviePlaylist,
    NewKinoheldCinemas,
    Parsers,
    RemovedKinoheldCinemas,
    Showtimes,
)

# Register your models here.
BLANK_CHOICE = (("", ""),)

# ____________________ CINEMAS ____________________

new_added_cinemas = []  # type: ignore
utc = pytz.UTC

from django.urls import path

# ____________________ MOVIE PLAYLISTS ______________


class PassThroughFilter(admin.SimpleListFilter):
    title = ""
    parameter_name = "cinema_id"
    template = "admin/hidden_filter.html"

    def lookups(self, request, model_admin):
        return ((request.GET.get(self.parameter_name), ""),)

    def queryset(self, request, queryset):
        return queryset


class MoviePlaylistAdmin(admin.ModelAdmin):
    list_display = [
        "ignore_movie",
        "poster_img",
        "title",
        "movie_id_res",
        "imdb_id",
        "tmdb_id",
        "poster",
        "photo",
        "imdb_rating",
        "list_premiere_date",
        "premiere_year",
        "distributor",
        "pg_rating",
        "duration",
        "media",
        "showtimes",
        "services",
        "genre",
        "bool_directors",
        "actors",
        "short_summary",
        "is_active_field",
    ]
    playlist_cinema_id = 0
    list_filter = (PassThroughFilter,)
    change_list_template = "admin/movieplaylist_change_list.html"

    def changelist_view(self, request, extra_context=None):
        if "cinema_id" in request.GET:
            self.playlist_cinema_id = (
                int(request.GET["cinema_id"])
                if request.GET["cinema_id"].isdecimal()
                else 0
            )

        cinema = Cinemas.objects.filter(pk=self.playlist_cinema_id)
        cinema_name = cinema[0].name if cinema.exists() else ""
        extra_context = {
            "title": f"Movie Playlist: {cinema_name}",
            "cinema": cinema.values()[0] if cinema.exists() else None,
        }
        return super().changelist_view(request, extra_context=extra_context)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(showtimes__cinema_id=self.playlist_cinema_id).distinct()

    def ignore_movie(self, obj):
        if obj.movie.ignore:
            return mark_safe("<a style='color:grey;'>IGNORED</a>")
        else:
            return mark_safe(
                f"<a href='/admin/cinemas/cinemas/ignore_movie/{obj.movie_id}'>Ignore this movie</a>"
            )

    def poster_img(self, obj):
        if obj.movie.poster_file_name:
            return mark_safe(
                f"<a href='/admin/cinemas/showtimes/?info_id={obj.id}&cinema_id={self.playlist_cinema_id}'>"
                f"<img src=https://s3-eu-west-1.amazonaws.com/kinode/production/movies/posters/{obj.movie_id}"
                f"/tiny.jpg style='max-width:140px'></img></a>"
            )
        else:
            return mark_safe(
                f"<a href='/admin/cinemas/showtimes/?info_id={obj.id}&cinema_id={self.playlist_cinema_id}'>"
                f"No photo</a>"
            )

    poster_img.short_description = ""  # type: ignore

    def movie_id_res(self, obj):
        return mark_safe(
            f'<a href="/admin/movies/movies/{obj.movie.id}/change/">{obj.movie.id}</a>'
        )

    movie_id_res.admin_order_field = "movie__id"  # type: ignore
    movie_id_res.short_description = "movie id"  # type: ignore

    def imdb_id(self, obj):
        return mark_safe(
            f'<a href="https://www.imdb.com/title/{obj.movie.imdb_id}/">{obj.movie.imdb_id}</a>'
        )

    imdb_id.admin_order_field = "movie__imdb_id"  # type: ignore

    def tmdb_id(self, obj):
        return mark_safe(
            f'<a href="https://www.themoviedb.org/movie/{obj.movie.tmdb_id}">{obj.movie.tmdb_id}</a>'
        )

    tmdb_id.admin_order_field = "movie__tmdb_id"  # type: ignore

    def poster(self, obj):
        return "✓" if obj.movie.poster_file_name else "✕"

    def photo(self, obj):
        return "✓" if obj.movie.photo_file_name else "✕"

    def imdb_rating(self, obj):
        return obj.movie.imdb_rating

    def premiere_year(self, obj):
        return obj.movie.premiere_date

    def distributor(self, obj):
        return obj.distributor.name

    def media(self, obj):
        return mark_safe(
            f'<a href="/admin/media/media/?media_connection_id={obj.id}">'
            f'{Media.objects.filter(media_connection_type="Info",media_connection_id=obj.id).count()}</a>'
        )

    def showtimes(self, obj):
        return mark_safe(
            f'<a href="/admin/cinemas/showtimes/?info_id={obj.id}&'
            f'cinema_id={self.playlist_cinema_id}">'
            f"{Showtimes.objects.filter(cinema_id=self.playlist_cinema_id, info_id=obj.id).count()}</a>"
        )

    def services(self, obj):
        return mark_safe(
            f'<a href="/admin/services/moviesservices/?info_id={obj.id}&">'
            f"{obj.movie_services.count()}</a>"
        )

    def genre(self, obj):
        return obj.movie.genre

    def bool_directors(self, obj):
        return "✓" if obj.directors else "✕"

    bool_directors.short_description = "directors"  # type: ignore

    def actors(self, obj):
        actors_count = (
            MoviesPeople.objects.filter(movie_id=obj.movie_id)
            .filter(person_role="actor")
            .count()
        )
        return "✓" if actors_count > 0 else "✕"

    def short_summary(self, obj):
        if obj.summary:
            return obj.summary[:200]

    def list_premiere_date(self, obj):
        return obj.premiere_date.date() if obj.premiere_date else "-"

    list_premiere_date.short_description = "premiere date"  # type: ignore

    def is_active_field(self, obj):
        if obj.active:
            return True


admin.site.register(MoviePlaylist, MoviePlaylistAdmin)

# ____________________ CINEMAS ______________


class CinemasForm(forms.ModelForm):
    active = forms.ChoiceField(choices=[], required=False)
    locale = forms.CharField(disabled=True)

    def __init__(self, *args, **kwargs):
        type = None

        chain_id = None
        ticket_url = None
        booking_url = None

        super().__init__(*args, **kwargs)



        self.fields["active"].label = mark_safe("<strong>Active</strong>")
        self.fields["active"].initial = self.fields["active"]
        self.fields["active"].choices = ((0, "0"), (1, "1"))
        self.fields["cinema_type"].choices = (
            ("cinema", "cinema"),
            ("occasional", "occasional"),
            ("open-air", "open air"),
            ("mobile", "mobile"),
            ("", ""),
        )



        if kwargs.get("instance"):
            type = kwargs.get("instance").cinema_type
            chain_id = kwargs.get("instance").chain_id
            ticket_url = kwargs.get("instance").default_ticket_url
            booking_url = kwargs.get("instance").default_url
        self.fields["cinema_type"].initial = type if type else ""
        self.fields["locale"].initial = "de"


        # enable to choose a chain's name from a list
        if chain_id:
            self.fields["chain"].initial = chain_id
            self.fields["chain"].label = mark_safe(f'<a href="/admin/cinemas/cinemas/?chain_id={chain_id}">Chain</a>')

        else:
            self.fields["chain"].choices = chain(
                 BLANK_CHOICE,
                 Chains.objects.all()
                 .values_list("id", "name")
                 .distinct()
                 .order_by("name"),
             )

        self.fields["chain"].required = False


        if ticket_url:
            self.fields["default_ticket_url"].label = mark_safe(
                f'<a href="{ticket_url}">Program URL</a>'
            )
        else:
            self.fields["default_ticket_url"].label = mark_safe("<strong>Program URL</strong></a>")


        if booking_url:
            self.fields["default_url"].label = mark_safe(
                f'<a href="{booking_url}">Cinema URL</a>'
            )
        else:

            self.fields["default_url"].label = mark_safe("<strong>Cinema URL</strong></a>")


    class Meta:
        model = Cinemas
        fields = "__all__"


class ActiveFilterCinemas(admin.SimpleListFilter):
    title = "Info status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active"),
            ("0", "Inactive"),
        )

    def queryset(self, request, queryset):

        if self.value() == "1":
            return queryset.filter(active="1")
        elif self.value() == "0":
            return queryset.filter(active="0")
        else:
            return queryset


class TypeFilterCinemas(admin.SimpleListFilter):
    title = "Cinema type"
    parameter_name = "cinema_type"

    def lookups(self, request, model_admin):
        return (
            ("cinema", "Cinema"),
            ("open-air", "Open air"),
            ("mobile", "Mobile"),
            ("occasional", "Occasional"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(cinema_type=self.value())
        else:
            return queryset


class ShowtimesFilterCinemas(admin.SimpleListFilter):
    title = "Showtimes"
    parameter_name = "showtimes"

    def lookups(self, request, model_admin):
        return (
            ("1", "With Showtimes"),
            ("0", "Without Showtimes"),
        )

    def queryset(self, request, queryset):
        cinemas_w_showtimes = (
            Showtimes.objects.all().distinct().values_list("cinema", flat=True)
        )
        if self.value() == "1":
            return queryset.filter(id__in=cinemas_w_showtimes)
        elif self.value() == "0":
            return queryset.exclude(id__in=cinemas_w_showtimes)
        else:
            return queryset

class LocaleFilterCinemas(admin.SimpleListFilter):
    title = "Locale"
    parameter_name = "locale"

    def lookups(self, request, model_admin):
        return (
            ("at","AT"),
            ("ch", "CH"),
            ("de","DE"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(locale = self.value())
        else:
            return queryset


class CinemasAdmin(admin.ModelAdmin):
    form = CinemasForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id_status",
        "get_chain_id",
        "chain_name",
        "name",
        "locale",
        "address",
        "post_code",
        "city",
        "has_url",
        "parser_type",
        "kinode_id",
        "parsers",
        "showtimes",
        "movie_playlist",
        "is_active_field",
    )
    list_per_page = 200
    search_fields = ("id", "name", "address", "post_code", "city")

    list_filter = (ActiveFilterCinemas,TypeFilterCinemas, ShowtimesFilterCinemas, LocaleFilterCinemas)
    readonly_fields = ("id","showtimes","movie_playlist","parsers")



    fields = (
        "id",
        "locale",
        "active",
        "chain",
        "cinema_type",
        "name",
        "short_name",
        "kinode_id",
        "kinode_app_id",
        "kinoheld_id",
        "kranki_id",
        "cinepass_id",
        "address",
        "post_code",
        "city",
        "longitude",
        "latitude",
        "phone",
        "default_url",
        "default_ticket_url",
        "parsers",
        "showtimes",
        "buffer",
        "movie_playlist",
        "note",
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('parsers','showtimes','chain', 'showtimes__movie')

    def is_active_field(self, obj):
        if obj.active == 1:
            return True
        elif obj.active == 0:
            return False

    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def parsers(self, obj):
        return format_html(
            '<a href="/admin/cinemas/parsers/?cinema_id=%s">%s</a>'
            % (obj.id, obj.parsers.all().count())
        )

    parsers.allow_tags = True  # type: ignore
    parsers.short_description = "Parsers"  # type: ignore

    def parser_type(self, obj):
        active_parser_for_cinema = [parser for parser in obj.parsers.all() if (parser.hour_queue==1 or parser.night_queue==1)]
        if len(active_parser_for_cinema)==1:
            return active_parser_for_cinema[0]

        return "-"

    def get_chain_id(self, obj):
        return format_html(
            '<a href="/admin/cinemas/chains/%s/change">%s</a>'
            % (obj.chain_id, obj.chain_id)
        ) if obj.chain_id else "-"

    get_chain_id.allow_tags = True  # type: ignore
    get_chain_id.short_description = "chain id"  # type: ignore

    def chain_name(self, obj):
        return obj.chain.name if obj.chain_id else None

    chain_name.allow_tags = True  # type: ignore
    chain_name.short_description = "chain name"  # type: ignore

    def showtimes(self, obj):
        st = obj.showtimes.all()
        st = len([s for s in st if s.movie.ignore == 0])
        return format_html(
            '<a href="/admin/cinemas/showtimes/?cinema_id=%s">%s</a>'
            % (obj.id, st)
        )

    showtimes.allow_tags = True  # type: ignore
    showtimes.short_description = "Showtimes"  # type: ignore

    def movie_playlist(self, obj):
        return format_html(
            '<a href="/admin/cinemas/movieplaylist/?cinema_id=%s">Movie Playlist</a>'
            % (obj.id)
        )

    movie_playlist.allow_tags = True  # type: ignore
    movie_playlist.short_description = "Movie playlist"  # type: ignore

    def has_url(self, obj):
        if obj.default_url:
            return format_html(f"<a href={obj.default_url}>↪</a>")
        else:
            return "-"

    has_url.short_description = "URL"  # type: ignore

    def response_change(self, request, obj):
        if not obj.active:
            obj.parsers.update(hour_queue=0, night_queue=0)
        return super(CinemasAdmin, self).response_change(request, obj)



# ____________________ NEW KINOHELD CINEMAS ______________


class NewKinoheldCinemasAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ____________________ REMOVED KINOHELD CINEMAS ______________


class RemovedKinoheldCinemasAdmin(admin.ModelAdmin):

    list_display = (
        "id_status",
        "kinoheld_id",
        "name",
        "address",
        "post_code",
        "city",
        "open_air",
        "kranki_id",
        "movie_playlist",
        "default_ticket",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def id_status(self, obj):
        return format_html(
            '<a href="/admin/cinemas/cinemas/%s/change/">%s</a>' % (obj.id, obj.id)
        )

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "id"  # type: ignore

    def default_ticket(self, obj):
        return format_html(
            "<a href=%s>%s</a>" % (obj.default_ticket_url, obj.default_ticket_url)
        )

    default_ticket.allow_tags = True  # type: ignore
    default_ticket.short_description = "default ticket url"  # type: ignore

    def open_air(self, obj):
        if obj.cinema_type == "open-air":
            return 1
        else:
            return 0

    open_air.allow_tags = True  # type: ignore
    open_air.short_description = "open air"  # type: ignore

    def movie_playlist(self, obj):
        return format_html(
            f'<a href="/admin/cinemas/movieplaylist/?cinema_id={obj.id}">Movie Playlist</a>'
        )

    movie_playlist.allow_tags = True  # type: ignore
    movie_playlist.short_description = "Movie playlist"  # type: ignore

    def get_queryset(self, request):
        ignored_cinemas_ids = [1032, 1307, 1581, 1589, 1591, 1621]
        api_cinemas_url = (
            "https://api.kinoheld.de/app/v1/cinemas?"
            "apikey=sfnp3blNVdT8WSH5fdVZ&all=1&ref=kinodeap"
        )
        s = requests.Session()
        response = s.get(api_cinemas_url)
        kinoheld_json = json.loads(response.text)

        kinoheld_ids = (
            Cinemas.objects.filter(
                locale="de",
                parsers__night_queue=True,
                parsers__parser_type="Kinoheld",
            )
            .exclude(id__in=ignored_cinemas_ids)
            .values_list("kinoheld_id", flat=True)
            .distinct()
        )

        a = set(kinoheld_ids) - set(kinoheld_json.keys())

        return Cinemas.objects.filter(
            Q(
                kinoheld_id__in=a,
                locale="de",
                parsers__night_queue=True,
            )
        ).exclude(id__in=ignored_cinemas_ids)


# ____________________ CHAINS ____________________


class ChainsForm(forms.ModelForm):

    locale = forms.CharField(disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["locale"].initial = "de"
        # self.fields["setting_group"] = forms.ModelChoiceField(
        #     queryset=SettingGroups.objects.filter(setting_type="area_types")
        #     .distinct()
        #     .order_by("setting_name"),
        #     required=False,
        # )
        # self.fields["setting_group"].label = "Setting group"

    class Meta:
        model = Chains
        fields = "__all__"
        exclude = ["created_at", "updated_at"]


class ChainsAdmin(admin.ModelAdmin):
    # raw_id_fields = [
    #     "setting_group",
    # ]
    form = ChainsForm
    change_form_template = "admin/button_change_form.html"
    list_display = ("id", "name", "locale", "priority", "cinemas")
    list_filter = (LocaleFilterCinemas,)
    search_fields = (
        "id",
        "name",
    )

    def cinemas(self, obj):
        return format_html(
            '<a href="/admin/cinemas/cinemas/?chain_id=%s">%s</a>'
            % (obj.id, obj.cinemas.count())
        )

    cinemas.allow_tags = True  # type: ignore
    cinemas.short_description = "Cinemas"  # type: ignore

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("priority")


# ____________________ CINEMAPARSERS ____________________
# curretly not visible in cms (maybe not needed?)


class CinemaParsersAdmin(admin.ModelAdmin):
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "name",
    )
    search_fields = (
        "id",
        "name",
    )


# ____________________ SHOWTIMES ____________________


class ShowtimesForm(forms.ModelForm):
    in_app_booking = forms.ChoiceField(choices=[], required=False)
    locale = forms.CharField(disabled=True)

    def __init__(self, *args, **kwargs):
        v = None
        info_id = None
        cinema_id = None
        movie_id = None
        ticket_url = None
        booking_url = None

        super().__init__(*args, **kwargs)
        self.fields["value"].choices = (
            ("3D", "3D"),
            ("4D", "4D"),
            ("OMU", "OmU"),
            ("OMEU", "OmeU"),
            ("OV", "OV"),
            ("", ""),
        )
        self.fields["movie"].required = False

        if kwargs.get("instance"):
            v = kwargs.get("instance").value
            ticket_url = kwargs.get("instance").ticket_link
            booking_url = kwargs.get("instance").booking_link

        elif kwargs.get("initial"):
            url_path = kwargs["initial"].get("_changelist_filters")
            if "info_id" in url_path:
                info_id = re.findall("info_id=\d+", url_path)
                if info_id:
                    info_id = info_id[0]
                    info_id = re.findall("\d+", info_id)[0]
                elif "%3D" in url_path:
                    info_id = url_path.split("%3D")[-1]

                info = Infos.objects.filter(id=info_id).first()
                movie_id = info.movie_id
            if "cinema_id" in url_path:
                cinema_id = re.findall("cinema_id=\d+", url_path)
                if cinema_id:
                    cinema_id = cinema_id[0]
                    cinema_id = re.findall("\d+", cinema_id)[0]
                elif "%3D" in url_path:
                    cinema_id = url_path.split("%3D")[-1]

        if ticket_url:
            self.fields["ticket_link"].label = mark_safe(
                f'<a href="{ticket_url}">Ticket link</a>'
            )
        else:
            self.fields["ticket_link"].label = mark_safe(
                "<strong>Ticket link</strong></a>"
            )

        if booking_url:
            self.fields["booking_link"].label = mark_safe(
                f'<a href="{booking_url}">Booking link</a>'
            )
        else:
            self.fields["booking_link"].label = mark_safe(
                "<strong>Booking link</strong></a>"
            )

        self.fields["value"].initial = v if v else ""
        self.fields["locale"].initial = "de"
        self.fields["info"].initial = info_id
        self.fields["cinema"].initial = cinema_id
        self.fields["movie"].initial = movie_id

        self.fields["cinema"].label = "Cinema id"
        self.fields["movie"].label = "Movie id"
        self.fields["info"].label = "Info id"
        self.fields["parser"].label = "Parser id"
        self.fields["in_app_booking"].choices = ((0, "0"), (1, "1"))

    def clean(self):
        data = self.cleaned_data
        if "info" in data and not data["movie"]:
            data["movie"] = Movies.objects.get(pk=data["info"].movie_id)
        if not data["movie"]:
            self._errors["movie"] = ErrorList(["This field is required."])
        return data

    class Meta:
        model = Showtimes
        fields = "__all__"


class TransferShowtimesForm(ActionForm):
    id_field = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_field"].label = "Cinema/Info id:"


class ShowtimesAdmin(admin.ModelAdmin):
    action_form = TransferShowtimesForm
    raw_id_fields = [
        "movie",
        "info",
        "cinema",
    ]
    form = ShowtimesForm
    change_form_template = "admin/button_change_form.html"
    add_form_template = "admin/add_showtimes_form.html"

    list_display = (
        "id_status",
        "date",
        "listd_value",
        "info_name",
        "get_movie_id",
        "info_link",
        "cinema_link",
        "cinema_name",
        "rss_address",
        "ticket_link_clickable",
        "cinema_playlist",
        "is_active_field",
    )

    actions = [
        "ignore_showtime",
        "delete_selected",
        "transfer_showtimes_to_another_info",
        "transfer_showtimes_to_another_cinema",
    ]

    search_fields = (
        "id",
        "cinema__id",
        "cinema__name",
        "movie__id",
        "movie__original_title",
        "info__id",
        "info__title",
        "movie__imdb_id",
    )
    readonly_fields = ("poster_tag", "id", "cinema_playlist")
    ordering = ["-date"]

    list_per_page = 200

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("info","movie","cinema","info__movie")
            .prefetch_related("cinema__parsers")
        )

    """
    def response_add(self, request, obj):
        start_date = obj.start_date
        end_date = obj.end_date
        hours = obj.hours
        if start_date and end_date and hours:
            dates_delta = end_date - start_date
            all_hours = hours.replace(" ", "").split(",")
            datetime_list = []
            for hour in all_hours:
                cur_hours = int(hour.split(":")[0])
                cur_minutes = int(hour.split(":")[1])
                for i in range(dates_delta.days + 1):
                    day = start_date + timedelta(days=i)
                    dt = datetime.combine(day, time(hour=cur_hours, minute=cur_minutes)).astimezone()
                    datetime_list.append(dt)
            for dt in datetime_list[::-1]:
                original_obj = obj
                original_obj.pk = None
                original_obj.id = None
                original_obj.date = dt
                original_obj.start_date = None
                original_obj.end_date = None
                original_obj.hours = None
                original_obj.save()
                print("generated",original_obj.__dict__)
            obj.date = datetime_list[0]
            obj.start_date = None
            obj.end_date = None
            obj.hours = None
            obj.save()
            print("instance",obj.__dict__)
            return HttpResponseRedirect("../")
        """

    def get_fieldsets(self, request, obj):
        self.fields = [
            "id",
            "poster_tag",
            "cinema",
            "movie",
            "info",
            "value",
            "date",
            "start_date",
            "end_date",
            "hours",
            "ticket_link",
            "booking_link",
            "cinema_playlist",
            "in_app_booking",
            "parser_type",
            "parser",
        ]
        if "change" in request.path:
            self.fields = [
                elem
                for elem in self.fields
                if elem not in ["start_date", "end_date", "hours"]
            ]
        return super(ShowtimesAdmin, self).get_fieldsets(request, obj)

    def ignore_showtime(self, request, queryset):
        for q in queryset:
            m = q.info.movie
            if m.ignore:
                m.ignore = 0
            else:
                m.ignore = 1
            m.save()
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    ignore_showtime.allow_tags = True  # type: ignore
    ignore_showtime.short_description = "(Un)Ignore selected"  # type: ignore

    def transfer_showtimes_to_another_info(self, request, queryset):
        info_id = request.POST["id_field"]
        try:
            info = Infos.objects.get(id=info_id)
        except:
            self.message_user(request, "Incorrect info id!", level=messages.ERROR)
        else:
            for q in queryset:
                q.movie_id = info.movie_id
                q.info_id = info.id
                q.save()

        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    transfer_showtimes_to_another_info.allow_tags = True  # type: ignore
    transfer_showtimes_to_another_info.short_description = "Transfer to another info ID"  # type: ignore

    def transfer_showtimes_to_another_cinema(self, request, queryset):
        cinema_id = request.POST["id_field"]
        try:
            cinema = Cinemas.objects.get(id=cinema_id)
        except:
            self.message_user(request, "Incorrect cinema id!", level=messages.ERROR)
        else:
            for q in queryset:
                q.cinema_id = cinema.id
                q.save()

        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    transfer_showtimes_to_another_cinema.allow_tags = True  # type: ignore
    transfer_showtimes_to_another_cinema.short_description = "Transfer to another cinema ID"  # type: ignore

    def is_active_field(self, obj):
        if obj.info.active:
            return True
        else:
            return False

    def id_status(self, obj):
        info = obj.info
        movie_ignored = info.movie.ignore
        if movie_ignored:
            return format_html(
                '<a style="color:Grey;" href="/admin/cinemas/showtimes/%s/change/">IGNORED</a>'
                % obj.id
            )
        elif obj.booking_link or obj.ticket_link:
            return format_html(
                f'<a style="color:#de8300;" href="/admin/cinemas/showtimes/{obj.id}/change/">{obj.id}</a>'
            )
        else:
            return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def cinema_link(self, obj):
        return format_html(
            '<a href="/admin/cinemas/cinemas/%s/change">%s</a>'
            % (obj.cinema_id, obj.cinema_id)
        )

    cinema_link.allow_tags = True  # type: ignore
    cinema_link.short_description = "cinema id"  # type: ignore

    def get_movie_id(self, obj):
        return format_html(
            '<a href="/admin/movies/movies/%s/change">%s</a>'
            % (obj.info.movie.id, obj.info.movie.id)
        )

    get_movie_id.allow_tags = True  # type: ignore
    get_movie_id.short_description = "Movie id"  # type: ignore

    def info_link(self, obj):
        return format_html(
            '<a href="/admin/movies/infos/%s/change">%s</a>'
            % (obj.info.id, obj.info.id)
        )

    info_link.allow_tags = True  # type: ignore
    info_link.short_description = "Info id"  # type: ignore

    def info_name(self, obj):
        return obj.info.title

    info_name.allow_tags = True  # type: ignore
    info_name.short_description = "Info name"  # type: ignore

    def cinema_name(self, obj):
        cinema = obj.cinema
        return mark_safe(f"<a href={cinema.default_ticket_url}>↪</a>")

    cinema_name.allow_tags = True  # type: ignore
    cinema_name.short_description = "Cinema URL"  # type: ignore

    def rss_address(self, obj):
        for parser in obj.cinema.parsers.all():
            if parser.cinema_id == obj.cinema_id and parser.parser_type == obj.parser_type:
                return mark_safe(f"<a href={parser.rss_address}>↪</a>")
        return "-"

    rss_address.allow_tags = True  # type: ignore
    rss_address.short_description = "Parser URL"  # type: ignore

    def ticket_link_clickable(self,obj):
        ticket_link = obj.ticket_link

        return mark_safe(f"<a href={ticket_link}>{ticket_link}</a>") if ticket_link else mark_safe("-")

    ticket_link_clickable.short_description = "ticket link"  # type: ignore

    def cinema_playlist(self, obj):
        return format_html(
            '<a href="/admin/cinemas/movieplaylist/?cinema_id=%s">Movie Playlist</a>'
            % (obj.cinema.id)
        )

    cinema_playlist.allow_tags = True  # type: ignore
    cinema_playlist.short_description = "cinema"  # type: ignore

    def date_formatted(self, obj):
        if obj.date:
            return obj.date.date()

    date_formatted.allow_tags = True  # type: ignore
    date_formatted.short_description = "date"  # type: ignore


    def listd_value(self,obj):
        return obj.value if obj.value else "-"

    listd_value.short_description = "value"


    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super(ShowtimesAdmin, self).get_search_results(
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


# ____________________ PARSERS ____________________


class ParsersForm(forms.ModelForm):

    hour_queue = forms.ChoiceField(choices=[], required=False)
    night_queue = forms.ChoiceField(choices=[], required=False)
    parser_type = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cinema_id = None
        rss_address = None

        self.fields["date"].label = "Run date"
        self.fields["cinema"].label = "Cinema id"
        self.fields["parser_type"].choices = (
            Parsers.objects.all()
            .values_list("parser_type", "parser_type")
            .distinct()
            .order_by("parser_type")
        )
        if kwargs.get("instance"):
            rss_address = kwargs.get("instance").rss_address

        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "cinema_id" in path:
                if "=" in path:
                    cinema_id = re.findall("cinema_id=\d+", path)
                    if cinema_id:
                        cinema_id = cinema_id[0]
                        cinema_id = re.findall("\d+", cinema_id)[0]
                elif "%3D" in path:
                    cinema_id = path.split("%3D")[-1]

        self.fields["cinema"].initial = cinema_id
        self.fields["hour_queue"].choices = ((0, "0"), (1, "1"))
        self.fields["night_queue"].choices = ((0, "0"), (1, "1"))

        if rss_address:
            self.fields["rss_address"].label = mark_safe(f"<a href={kwargs.get('instance').rss_address}><strong>RSS Address</strong></a>")

    class Meta:
        model = Parsers
        fields = "__all__"
        exclude = ["created_at", "updated_at"]


class ActiveFilterParsers(admin.SimpleListFilter):
    title = "Info status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active"),
            ("0", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(Q(hour_queue="1") | Q(night_queue="1"))
        elif self.value() == "0":
            return queryset.filter(Q(hour_queue="0") & Q(night_queue="0"))
        else:
            return queryset


class ParserLogs(admin.SimpleListFilter):
    title = "Parser logs"
    parameter_name = "logs"

    def lookups(self, request, model_admin):
        return (
            ("not_executed", "Running interrupted"),
            ("timeout", "Timeout"),
            ("twin_movies", "Detected more movies with same title"),
        )

    def queryset(self, request, queryset):
        if self.value() == "not_executed":
            return queryset.filter(Q(hour_queue="1") | Q(night_queue="1")).filter(
                date__lt=utc.localize(datetime.now()) - timedelta(days=1)
            )
        elif self.value() == "timeout":
            return queryset.filter(Q(hour_queue="1") | Q(night_queue="1")).filter(
                last_log__icontains="timeout::error"
            )
        elif self.value() == "twin_movies":
            return queryset.filter(Q(hour_queue="1") | Q(night_queue="1")).filter(
                last_log__icontains="chosen info is"
            )

# parser filters for errors, alerts and warnings:

class ParserErrorFilter(admin.SimpleListFilter):
    title = "Parser error"
    parameter_name = "error_log"

    def lookups(self, request, model_admin):
        return (
            ("error", "Parsers with errors"),
            
        )

    def queryset(self, request, queryset):
        if self.value() == "error":
            return queryset.filter((~Q(error_log = None) & ~Q(error_log ="")), (Q(hour_queue=1) | Q(night_queue=1)), cinema__locale="de")
        else:
            return queryset

class ParserWarningFilter(admin.SimpleListFilter):
    title = "Parser warning"
    parameter_name = "warning"
    

    def lookups(self, request, model_admin):
        return (
            ("warning", "Parsers with warning"),
            
        )
    def queryset(self, request, queryset):
        if self.value() == "warning":
            return queryset.filter((Q(night_queue = 1) | Q(hour_queue = 1)), number_of_showtimes__lt = F('cinema__buffer'), number_of_showtimes__gt = 0, cinema__locale="de").order_by("-updated_at")
        else:
            return queryset

class ParserAlertFilter(admin.SimpleListFilter):
    title = "Parser alert"
    parameter_name = "alert"
    

    def lookups(self, request, model_admin):
        return (
            ("alert", "Parsers with alert"),
            
        )

    def queryset(self, request, queryset):
        if self.value() == "alert":
            return queryset.filter(Q(number_of_showtimes= 0) & (Q(hour_queue = 1) | Q(night_queue = 1)), cinema__locale="de").order_by("-updated_at")
        else:
            return queryset
           
            
@admin.action(description='(De)Activate selected parsers')
def de_activate_parsers(modeladmin, request, queryset):
    for el in queryset:
        if el.hour_queue or el.night_queue:
            el.hour_queue=0
            el.night_queue=0
            el.save(update_fields=["hour_queue","night_queue"])
        else:
            el.hour_queue=1
            el.night_queue=1
            el.save(update_fields=["hour_queue","night_queue"])

class ParsersAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "cinema",
    ]
    form = ParsersForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id_status",
        "cinema_link",
        "status_parser_type",
        "cinema_name",
        "city",
        "showtimes",
        "change_hour_queue",
        "change_night_queue",
        "has_rss_address",
        "list_rundate",
        "priority",
        "is_active_field",
        "run_parser"
    )
    list_per_page = 200
    search_fields = ("id","parser_type__icontains","rss_address__icontains")
    list_filter = (ActiveFilterParsers, ParserLogs, ParserErrorFilter, ParserWarningFilter, ParserAlertFilter, "parser_type")
    readonly_fields = ("id","run_parser")
    actions = [de_activate_parsers]

    fields = (
        "run_parser",
        "id",
        "cinema",
        "parser_type",
        "rss_address",
        "date",
        "hour_queue",
        "night_queue",
        "last_log",
        "error_log",
        "note",
        "priority",
        "in_app_booking",
        "custom_attributes",
        "queue",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cinema').prefetch_related('cinema__showtimes').annotate(number_of_showtimes=Count('cinema__showtimes'))

    def status_parser_type(self,obj):
        if (obj.hour_queue or obj.night_queue) and obj.cinema.showtimes.count() == 0:
            return mark_safe(f'<span style="color:#c533ff">{obj.parser_type}</span>')
        else:
            return obj.parser_type
    status_parser_type.short_description = "Parser type"
    status_parser_type.admin_order_field = "parser_type"

    def is_active_field(self, obj):
        if obj.night_queue or obj.hour_queue:
            return True
        else:
            return False

    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def cinema_link(self, obj):
        return format_html(
            '<a href="/admin/cinemas/cinemas/%s/change">%s</a>'
            % (obj.cinema_id, obj.cinema_id)
        )

    cinema_link.allow_tags = True  # type: ignore
    cinema_link.short_description = "cinema id"  # type: ignore

    def city(self, obj):
        return obj.cinema.city

    city.allow_tags = True  # type: ignore
    city.short_description = "City"  # type: ignore

    def showtimes(self, obj):
        if (obj.hour_queue or obj.night_queue) and len(obj.cinema.showtimes.all()) == 0:
            return format_html(
                '<a href="/admin/cinemas/showtimes/?cinema_id=%s" style="color:#c533ff">%s</a>'
                % (obj.cinema_id, obj.cinema.showtimes.count())
            )
        else:
            return format_html(
                '<a href="/admin/cinemas/showtimes/?cinema_id=%s">%s</a>'
                % (obj.cinema_id, obj.cinema.showtimes.count())
            )

    showtimes.allow_tags = True  # type: ignore
    showtimes.short_description = "Showtimes"  # type: ignore
    showtimes.admin_order_field = '-number_of_showtimes'

    def cinema_name(self, obj):
        return obj.cinema.name

    cinema_name.allow_tags = True  # type: ignore
    cinema_name.short_description = "Cinema name"  # type: ignore

    def change_hour_queue(self, obj):
        if obj.cinema.showtimes.count() == 0:
            return mark_safe("<span style='color:#c533ff'>ON</span>") if obj.hour_queue == 1 else "OFF"
        else:
            return "ON" if obj.hour_queue == 1 else "OFF"

    change_hour_queue.allow_tags = True  # type: ignore
    change_hour_queue.short_description = "hour q"  # type: ignore

    def change_night_queue(self, obj):
        if obj.cinema.showtimes.count() == 0:
            return mark_safe("<span style='color:#c533ff'>ON</span>") if obj.night_queue == 1 else "OFF"
        else:
            return "ON" if obj.night_queue == 1 else "OFF"

    change_night_queue.allow_tags = True  # type: ignore
    change_night_queue.short_description = "night q"  # type: ignore

    def has_rss_address(self, obj):
        if obj.rss_address:
            return format_html(f"<a href={obj.rss_address}>{obj.rss_address}</a>")
        else:
            return "✕"

    has_rss_address.short_description = "Parser URL"  # type: ignore

    def list_rundate(self, obj):
        return obj.date

    list_rundate.short_description = "Run date"  # type: ignore

    def run_parser(self, obj):
        c_id = str(obj.cinema_id)
        parser_type = obj.parser_type
        parser_name = rundeck_available_one_cinema_parsers.get(parser_type, None)

        button_html = f"""<input id="run_job{parser_name}{c_id}" type="button" value="Run job" onclick="window.location.href='/admin/cinemas/cinemas/run_parser?parser_name={parser_name}&cinema_id={c_id}'"/>"""

        return mark_safe(button_html) if parser_name else format_html("<div style='margin:auto;text-align: center;'>Not available</div>")

    run_parser.short_description = "Rundeck"


rundeck_available_one_cinema_parsers = {
    "AkaFilmclub":"aka_filmclub",
    "AlabamaKino": "alabama_kino",
    "AstorBerlin":"astor",
    "Atrada":"atrada",
    "AutokinoLangenhessen2":"autokino_langenhessen",
    "BonnerKinemathek":"bonner_kinemathek",
    "CafeBeck":"cafe_beck",
    "CentralkinoLingen":"centralkino_lingen",
    "CineWebNew":"cine_web_new",
    "Cinecitta":"cinecitta",
    "Cineding":"cindeing",
    "CinemaBoppard":"cinema_boppard",
    "Cinemaxx":"cinemaxx",
    "Cinemayence2":"cinemayence",
    "Cineorder":"cineorder",
    "Cineplex":"cineplex",
    "CineprogJson":"cineprog_json",
    "CinestarNew":"cinestar",
    "Cinetixx":"cinetixx",
    "Cinster":"cinster",
    "CityKinos":"citykino",
    "ClubkinoSiegmar":"clubkino_siegmar",
    "ClubKinoGlauchau":"club_kino_glauchau",
    "ClubManufaktur":"club_manufaktur",
    "CobraSolingen":"cobra_solingen",
    "Critic":"critic",
    "Dampfsaeg":"dampfsaeg",
    "EifelFilmBuhne":"eifel_film_buhne",
    "EschbornKino":"eschborn_kino",
    "EuropaPark":"europa_park",
    "FilmeImSchloss":"filme_im_schloss",
    "FilmmuseumPotsdam":"filmmuseum_potsdam",
    "FilmForum":"film_forum",
    "Filmburg":"filmburg",
    "FilmclubComma":"filmclub_comma",
    "FilmEck":"film_eck",
    "FilmtheaterHasetor":"filmtheater_hasetor",
    "FilmstudioRwth":"filmstudio_rwth",
    "ForumCinemas":"forum_cinemas",
    "FontaneKlub":"fontane_klub",
    "GucklochKino":"guckloch_kino",
    "GrossGerau":"grossgerau",
    "Hallenbad":"hallenbad",
    "HannoverDe":"hannover_de",
    "HarmonieLichtspiele":"harmonie_lichtspiele",
    "Indiekino":"indiekino",
    "KiezKino":"kiezkino",
    "KinemathekKarlsruhe":"kinemathek_karlsruhe",
    "KinoAlteMuhle":"kino_alte_muhle",
    "KinoGelnhausen":"kino_gelnhausen",
    "Kino35":"kino35",
    "KinoAnklam":"kino_anklam",
    "KinoDiessen":"kino_diessen",
    "KinoLoeningen":"kino_loeningen",
    "KinoPlochingen":"kino_plochingen",
    "KinotreffLichtblick":"kinotreff_lichtblick",
    "Kinoheld":"kinoheld",
    "KinoheldNomad":"kinoheld_nomad",
    "KinoImGriesbraeu":"kinoimgriesbraeu",
    "KinoImSprengel":"kino_im_sprengel",
    "Gehrenberg":"gehrenberg",
    "Kinoimschafstall2":"kinoimschafstall",
    "KinoKultur":"kino_kultur",
    "KinomobilBw":"kinomobil_bw",
    "Kinomonami":"kinomonami",
    "KinoOberviechtach":"kino_oberviechtach",
    "Kinopolis":"kinopolis",
    "Kinoschaumburg":"kinoschaumburg",
    "KinoticketsOnline":"kinotickets_online",
    "KinoTaucha":"kino_taucha",
    "KinoGrenzlandLichtspiele":"kino_grenzland_lichtspiele",
    "KinoCafeBar": "kino_cafe_bar",
    "KinoZeit":"kino_zeit",
    "KinoZeven":"kino_zeven",
    "KirRow":"kirrow",
    "KlappeDieZweite":"klappe_die_zweite",
    "KokiOberkirch":"koki_oberkirch",
    "KronenLichtspiele":"kronen_lichtspiele",
    "KurLichtspiele":"kurlichtspiele",
    "Kunstbauerkino":"kunstbauer_kino",
    "Lichtspielhaus":"lichtspielhaus",
    "Leinepark":"leinepark",
    "LichtspieleMoessingen":"lichtspiele_moessingen",
    "LosheimStausee":"losheim_stausee",
    "LuxorKino":"luxor_kino",
    "Malzhaus":"malzhaus",
    "MetropolFallersleben":"metropol_fallersleben",
    "MetropolisFilmtheater":"metropolis_filmtheater",
    "Magazinfilmkunst":"magazin_filmkunst",
    "MariasKino":"marias_kino",
    "MobilesKino":"mobileskino",
    "DresdenFilmnaechte":"dresden_filmnaechte",
    "KinoLatuecht":"kino_latucht",
    "Orfeos2":"orfeos",
    "Platenlaase":"platenlaase",
    "Pelmke":"pelmke",
    "ProgrammkinosMainz":"programm_kinos_mainz",
    "Pupille":"pupille",
    "RexSchifferstadt":"rexschifferstadt",
    "Reichenstrasse":"reichenstrasse",
    "Rhythmusfilm":"rhythmusfilm",
    "RitterhuderLichtspiele":"ritterhuder_lichtspiele",
    "Schaustall":"schaustall",
    "SchlossDankern":"schloss_dankern",
    "Steinhaus":"steinhaus",
    "StadtheaterLandsberg":"stadtheater_landsberg",
    "TicketCloud":"ticket_cloud",
    "UciKinowelt":"uci_kinowelt",
    "UniversalMovieBoxDaysInRows":"universal_movie_box_days_in_rows",
    "Universum":"universum",
    "Uferpalast":"uferpalast",
    "VhsEmden":"vhs_emden",
    "Yorck":"yorck",
    "ZeliZetel":"zelizetel",
}


# ____________________ KINOHELD ____________________

# in progress
# class NewlyAddedFilter(admin.SimpleListFilter):
#     title = ('Info status')
#
#     def lookups(self, request, model_admin):
#         return (
#             (True, 'Missing'),
#             (False, 'Removed'),
#         )
#
#     def queryset(self, request, queryset):
#         ignored_cinemas_ids = [1032, 1307, 1581, 1589, 1591, 1621]
#         api_cinemas_url = "https://api.kinoheld.de/app/v1/cinemas?" \
#                           "apikey=sfnp3blNVdT8WSH5fdVZ&all=1&ref=kinodeap"
#         s = requests.Session()
#         response = s.get(api_cinemas_url)
#         kinoheld_json = json.loads(response.text)
#
#         missing_cinemas = []
#         for c_id in kinoheld_json:
#             cinema = kinoheld_json[c_id]
#             if not Cinemas.objects.filter(kinoheld_id=c_id) \
#                     and int(c_id) not in ignored_cinemas_ids:
#                 missing_cinemas.append(cinema)
#
#         if self.value() == '1':
#             return queryset.filter(active='1')
#         elif self.value() == '0':
#             return queryset.filter(active='0')
#         else:
#             return queryset.filter(active='0')


# class StatusFilter(admin.SimpleListFilter):
#     title = ('Info status')
#     parameter_name = 'kinoheld_id'
#
#     def lookups(self, request, model_admin):
#         return (
#             ('2', 'Newly Added'),
#             ('1', 'Active'),
#             ('0', 'Removed'),
#         )
#
#     def queryset(self, request, queryset):
#         ignored_cinemas_ids = [1032, 1307, 1581, 1589, 1591, 1621]
#         api_cinemas_url = "https://api.kinoheld.de/app/v1/cinemas?" \
#                           "apikey=sfnp3blNVdT8WSH5fdVZ&all=1&ref=kinodeap"
#         s = requests.Session()
#         response = s.get(api_cinemas_url)
#         kinoheld_json = json.loads(response.text)
#
#         removed_cinemas = []
#         for cinema in Cinemas.objects.all():
#             k_id = cinema.kinoheld_id
#             if k_id is not None and k_id is not '' and \
#                     k_id not in kinoheld_json.keys():
#                 removed_cinemas.append(k_id)
#
#         missing_cinemas = []
#         kinoheld_ids = Cinemas.objects.all().values_list(
#             'kinoheld_id', flat=True).distinct()
#         for c_id in kinoheld_json:
#             if c_id is not '' and c_id is not None and c_id not in kinoheld_ids \
#                     and int(c_id) not in ignored_cinemas_ids \
#                     and int(c_id) not in new_added_cinemas:
#                 missing_cinemas.append(kinoheld_json[c_id])
#                 new_added_cinemas.append(int(c_id))
#
#         new_kinoheld_ids = []
#         for c in missing_cinemas:
#             new_cinema = Cinemas(
#                 locale='de',
#                 name=c['cinema_name'],
#                 address=c['street'],
#                 default_ticket_url=c['deeplink'],
#                 created_at=utc.localize(datetime.now()),
#                 updated_at=utc.localize(datetime.now()),
#                 longitude=c['longitude'],
#                 latitude=c['latitude'],
#                 post_code=c['postcode'],
#                 city=c['city'],
#                 kranki_id=c['kranki_id'],
#                 kinoheld_id=c['cinema_id'],
#                 active=0
#             )
#             new_cinema.save()
#             new_kinoheld_ids.append(c['cinema_id'])
#
#         new_kinoheld_ids
#
#         if self.value() == '1':
#             return queryset.filter(~Q(kinoheld_id__in=removed_cinemas))
#         elif self.value() == '0':
#             return queryset.filter(kinoheld_id__in=removed_cinemas)
#         elif self.value() == '2':
#             return queryset.filter(kinoheld_id__in=new_kinoheld_ids)
#         else:
#             return queryset


# class KinoheldAdmin(admin.ModelAdmin):
#     change_form_template = 'admin/button_change_form.html'
#     list_display = (
#         'id', 'kinoheld_id', 'name', 'address', 'post_code', 'city',
#         'kranki_id', 'default_url'
#     )
#     list_filter = (StatusFilter,)

admin.site.register(Cinemas, CinemasAdmin)
admin.site.register(NewKinoheldCinemas, NewKinoheldCinemasAdmin)
admin.site.register(RemovedKinoheldCinemas, RemovedKinoheldCinemasAdmin)
admin.site.register(Chains, ChainsAdmin)
# admin.site.register(CinemaParsers, CinemaParsersAdmin)
admin.site.register(Parsers, ParsersAdmin)
admin.site.register(Showtimes, ShowtimesAdmin)
