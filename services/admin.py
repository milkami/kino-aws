from datetime import datetime
import re
from itertools import chain

from django import forms
from django.contrib import admin
from django.utils.html import format_html, mark_safe

from movies.models import Infos, Movies
from tvshows.models import Seasons, SeasonTranslations, TvShows, TvShowTranslations

from .models import MoviesServices, SeasonServices, Services
from django.contrib.admin.helpers import ActionForm
from django.http import HttpResponseRedirect

# Register your models here.
BLANK_CHOICE = (("", ""),)


class ServicesForm(forms.ModelForm):
    active = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["active"].label = mark_safe("<strong>Active</strong>")
        self.fields["active"].initial = self.fields["active"]
        self.fields["active"].choices = ((0, "0"), (1, "1"))

    class Meta:
        model = Services
        fields = "__all__"
        exclude = ["created_at", "updated_at"]

class ActiveServicesFilter(admin.SimpleListFilter):
    title = "service status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return [("1","Active"),("0","Not Active")]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(active=self.value())
        else:
            return queryset


class ServicesAdmin(admin.ModelAdmin):
    form = ServicesForm
    ordering = ["-priority"]
    list_display = (
        "id",
        "priority",
        "name",
        "service_type",
        "web_clickable",
        "movies_services_link",
        "season_services_link",
        "tos_clickable",
        "is_active_field"
    )
    search_fields = ("id", "name")
    list_filter = ("service_type",ActiveServicesFilter)  # 'priority',)

    def is_active_field(self,obj):
        return True if obj.active else False

    def movies_services_link(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?service_id=%s">%s</a>'
            % (obj.id, obj.movie_services.filter(service_id=obj.id).count())
        )
    movies_services_link.allow_tags = True  # type: ignore
    movies_services_link.short_description = "movies services"  # type: ignore

    def web_clickable(self, obj):
        return mark_safe(f"<a href={obj.web}>{obj.web}</a>")
    web_clickable.short_description = "web"

    def tos_clickable(self, obj):
        return mark_safe(f"<a href={obj.tos}>{obj.tos}</a>")
    tos_clickable.short_description = "tos"



    def season_services_link(self, obj):
        return format_html(
            '<a href="/admin/services/seasonservices/?service_id=%s">%s</a>'
            % (obj.id, obj.season_services.filter(service_id=obj.id).count())
        )

    season_services_link.allow_tags = True  # type: ignore
    season_services_link.short_description = "season services"  # type: ignore


# ____________________ SEASON SERVICES ____________________


class SeasonServicesForm(forms.ModelForm):

    locale = forms.CharField(disabled=True, required=False)
    service_name = forms.CharField(disabled=True, required=False)
    flat = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        service_id = None
        tv_show_translation_id = None
        tv_show_id = None
        service_name = None
        tv_show = None
        season_id = None
        season_translation_id = None
        tv_show_instance = None
        tv_show_translation_instance = None
        season_instance = None
        season_translation_instance = None
        service_instance = None
        link=None

        if kwargs.get("instance"):
            service_id = kwargs.get("instance").service_id
            link = kwargs.get("instance").link

        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "service_id" in path:
                if "=" in path:
                    service_id = re.findall("service_id=\d+", path)
                    if service_id:
                        service_id = service_id[0]
                        service_id = re.findall("\d+", service_id)[0]
                elif "%3D" in path:
                    service_id = path.split("%3D")[-1]

            if "tv_show_translation_id" in path:
                if "=" in path:
                    tv_show_translation_id = re.findall(
                        "tv_show_translation_id=\d+", path
                    )
                    if tv_show_translation_id:
                        tv_show_translation_id = tv_show_translation_id[0]
                        tv_show_translation_id = re.findall(
                            "\d+", tv_show_translation_id
                        )[0]
                elif "%3D" in path:
                    tv_show_translation_id = path.split("%3D")[-1]

                tv_show_translation_instance = TvShowTranslations.objects.filter(
                    id=tv_show_translation_id
                ).first()

                tv_show_instance = tv_show_translation_instance.tv_show

                tv_show_translation_id = tv_show_translation_instance.id
                tv_show_id = tv_show_instance.id

            if "tv_show_id" in path:
                if "=" in path:
                    tv_show_id = re.findall("tv_show_id=\d+", path)
                    if tv_show_id:
                        tv_show_id = tv_show_id[0]
                        tv_show_id = re.findall("\d+", tv_show_id)[0]
                elif "%3D" in path:
                    tv_show_id = path.split("%3D")[-1]

                tv_show_instance = TvShows.objects.filter(id=tv_show_id).first()

            if "season_id" in path:
                if "=" in path:
                    season_id = re.findall("season_id=\d+", path)
                    if season_id:
                        season_id = season_id[0]
                        season_id = re.findall("\d+", season_id)[0]
                elif "%3D" in path:
                    season_id = path.split("%3D")[-1]

                season_instance = Seasons.objects.filter(id=season_id).first()
                tv_show_instance = season_instance.tv_show
                tv_show_id = tv_show_instance.id

        if tv_show_instance:
            self.fields[
                "tv_show_translation"
            ].queryset = tv_show_instance.tv_show_translations
            self.fields["season"].queryset = tv_show_instance.seasons
            self.fields[
                "season_translation"
            ].queryset = tv_show_instance.seasons.values_list(
                "season_translations__title", flat=True
            )

            if tv_show_instance.tv_show_translations.all().count() == 1:
                self.fields["tv_show_translation"].initial = (
                    tv_show_instance.tv_show_translations.all().first().id
                )
            else:
                self.fields["tv_show_translation"].label = mark_safe(
                    f"<a href='/admin/tvshows/tvshowtranslations/?tv_show_id={tv_show_instance.id}'>Tv show translation</a>"
                )

        if season_instance:
            self.fields["season_number"].initial = season_instance.season_number
            self.fields[
                "season_translation"
            ].queryset = season_instance.season_translations

            if season_instance.season_translations.all().count() == 1:
                self.fields["season_translation"].initial = (
                    season_instance.season_translations.all().first().id
                )
            else:
                self.fields["season_translation"].label = mark_safe(
                    f"<a href='/admin/tvshows/seasontranslations/?season_id={season_instance.id}'>Season translation</a>"
                )

        if service_id:
            self.fields["service"].initial = service_id
        else:
            self.fields["service"].choices = chain(
                BLANK_CHOICE,
                Services.objects.all()
                .values_list("id", "name")
                .distinct()
                .order_by("name"),
            )
        if tv_show_translation_id:
            self.fields["tv_show_translation"].initial = tv_show_translation_id
        self.fields["tv_show"].initial = tv_show_id
        self.fields["season"].initial = season_id
        self.fields["locale"].initial = "de"
        self.fields["service_name"].initial = service_name

        self.fields["service_season_id"].label = mark_safe(
            "<strong>Service season id</strong>"
        )
        self.fields["service"].label = mark_safe("<strong>Service</strong>")
        self.fields["flat"].label = mark_safe("<strong>Flat</strong>")
        self.fields["flat"].initial = self.fields["flat"]
        self.fields["flat"].choices = ((0, "0"), (1, "1"))
        self.fields["link"].label = mark_safe("<strong>Link</strong>")
        self.fields["buy_price"].label = mark_safe("<strong>Buy price</strong>")
        self.fields["rent_price"].label = mark_safe("<strong>Rent price</strong>")
        self.fields["prices"].label = mark_safe("<strong>Prices</strong>")
        self.fields["available_from"].label = mark_safe(
            "<strong>Available from</strong>"
        )
        self.fields["available_until"].label = mark_safe(
            "<strong>Available until</strong>"
        )
        self.fields["tv_show"].label = mark_safe("<strong>Tv show</strong>")
        self.fields["season"].label = mark_safe("<strong>Season</strong>")
        self.fields["season_translation"].label = mark_safe(
            "<strong>Season translation</strong>"
        )

        if link:
            self.fields["link"].label = mark_safe(f"<a href={kwargs.get('instance').link}><strong>Link</strong></a>")

    class Meta:
        model = SeasonServices
        fields = "__all__"
        exclude = ["created_at", "updated_at"]

class TransferSeasonServicesForm(ActionForm):
    id_field = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_field"].label = "Season id:"


class SeasonServicesAdmin(admin.ModelAdmin):
    action_form = TransferSeasonServicesForm
    ordering = ["-updated_at"]
    raw_id_fields = ["tv_show", "tv_show_translation", "season", "season_translation"]
    form = SeasonServicesForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id_status",
        "tvshow_name",
        "service_name",
        "seasons_service",
        "short_season_number",
        "tvshow_link",
        "tvshow_translation_link",
        "available_from",
        "available_until",
        "updated_at",
        "value_list",
        "types_list",
        "prices_list",
        "is_active_field",
    )
    search_fields = (
        "id",
        "tv_show__original_title",
    )
    # list_filter = (ServiceIdFilter, 'tv_show_translation_id',
    #               'tv_show_id', 'season_id')

    list_filter = ()

    readonly_fields = ("id",)

    fields = (
        "id",
        "tv_show",
        "tv_show_translation",
        "service",
        "locale",
        "season_number",
        "season",
        "service_season_id",
        "season_translation",
        "flat",
        "link",
        "buy_price",
        "rent_price",
        "prices",
        "available_from",
        "available_until",
    )

    actions = [
        "delete_selected",
        "transfer_seasonservice_to_another_season",
    ]
    list_per_page = 20

    def transfer_seasonservice_to_another_season(self, request, queryset):
        season_id = request.POST["id_field"]
        try:
            season = Seasons.objects.get(id=season_id)
            tv_show_translation_id = season.tv_show.tv_show_translations.first().id
            season_translation_id = season.season_translations.first().id
        except:
            self.message_user(request, "Incorrect Season ID!", level=40)
            return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")
        
        queryset.update(
                tv_show_id=season.tv_show_id,
                tv_show_translation_id=tv_show_translation_id,
                season_id = season_id,
                season_translation_id = season_translation_id,
                updated_at=datetime.now().astimezone()
                )
        self.message_user(request, f"{queryset.count()} Season services updated!", level=25)
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")
    
    transfer_seasonservice_to_another_season.allow_tags = True  # type: ignore
    transfer_seasonservice_to_another_season.short_description = "Transfer to another season ID"  # type: ignore

    def get_queryset(self, request):
        service_id = request.GET.get("service_id", None)
        qs = (super().get_queryset(request)
                .select_related("tv_show","service","tv_show_translation")
                #.prefetch_related("tv_show","service","tv_show_translation")
            )
        if service_id:
            return qs.filter(service_id=service_id)
        return qs

    def short_season_number(self, obj):
        return obj.season_number

    short_season_number.short_description = "#"

    def value_list(self, obj):
        if obj.prices:
            values_list = re.findall("HD|SD|4K", obj.prices)
            return ", ".join(values_list)
        else:
            return ""

    value_list.allow_tags = True  # type: ignore
    value_list.short_description = "value"  # type: ignore

    def types_list(self, obj):
        if obj.prices:
            values_list = re.findall("rent|buy|flat", obj.prices)
            return ", ".join(values_list)
        else:
            return ""

    types_list.allow_tags = True  # type: ignore
    types_list.short_description = "type"  # type: ignore

    def prices_list(self, obj):
        if obj.prices:
            values_list = re.findall("\d+.\d+", obj.prices)
            return ", ".join(values_list)
        else:
            return ""

    prices_list.allow_tags = True  # type: ignore
    prices_list.short_description = "price"  # type: ignore

    def seasons_service(self, obj):
        return format_html("<a href=%s>%s</a>" % (obj.link, obj.service_season_id))

    seasons_service.allow_tags = True  # type: ignore
    seasons_service.short_description = "service season id"  # type: ignore

    def is_active_field(self, obj):
        if obj.tv_show_translation.active:
                return True
        return False
        
    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def service_name(self, obj):
        return obj.service.name

    service_name.allow_tags = True  # type: ignore
    service_name.short_description = "service name"  # type: ignore

    def tvshow_link(self, obj):
        return format_html(
            '<a href="/admin/tvshows/tvshows/%s/change">%s</a>'
            % (obj.tv_show_id, obj.tv_show_id)
        )

    tvshow_link.allow_tags = True  # type: ignore
    tvshow_link.short_description = "tvshow id"  # type: ignore

    def tvshow_translation_link(self, obj):
        return format_html(
            '<a href="/admin/tvshows/tvshowtranslations/%s/change">%s</a>'
            % (obj.tv_show_translation_id, obj.tv_show_translation_id)
        )

    tvshow_translation_link.allow_tags = True  # type: ignore
    tvshow_translation_link.short_description = "translation id"  # type: ignore

    def tvshow_name(self, obj):
        return obj.tv_show.original_title

    tvshow_name.allow_tags = True  # type: ignore
    tvshow_name.short_description = "tv show name"  # type: ignore

    # def get_queryset(self, request):
    #     service = Services.objects.filter(id=request.GET.get("service_id")).first()
    #     if service:
    #         return service.season_services.all()
    #     else:
    #         return SeasonServices.objects.all()


# ____________________ MOVIES SERVICES ____________________


class MoviesServicesForm(forms.ModelForm):

    locale = forms.CharField(disabled=True, required=False)
    flat = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        service_id = None
        info_id = None
        movie_id = None
        movie_instance = None
        info_instance = None

        if kwargs.get("instance"):
            service_id = kwargs.get("instance").service_id

        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "service_id" in path:
                if "=" in path:
                    service_id = re.findall("service_id=\d+", path)
                    if service_id:
                        service_id = service_id[0]
                        service_id = re.findall("\d+", service_id)[0]
                elif "%3D" in path:
                    service_id = path.split("%3D")[-1]

            if "info_id" in path:
                if "=" in path:
                    info_id = re.findall("info_id=\d+", path)
                    if info_id:
                        info_id = info_id[0]
                        info_id = re.findall("\d+", info_id)[0]
                elif "%3D" in path:
                    info_id = path.split("%3D")[-1]

                info_instance = Infos.objects.filter(id=info_id).first()
                movie_instance = info_instance.movie
                movie_id = movie_instance.id

            if "movie_id" in path:
                if "=" in path:
                    movie_id = re.findall("movie_id=\d+", path)
                    if movie_id:
                        movie_id = movie_id[0]
                        movie_id = re.findall("\d+", movie_id)[0]
                elif "%3D" in path:
                    movie_id = path.split("%3D")[-1]

                movie_instance = Movies.objects.filter(id=movie_id).first()

        if movie_instance:
            self.fields["info"].queryset = movie_instance.infos

            if movie_instance.infos.all().count() == 1:
                self.fields["info"].initial = movie_instance.infos.all().first().id
            else:
                self.fields["info"].label = mark_safe(
                    f"<a href='/admin/movies/infos/?movie_id={movie_instance.id}'>Info</a>"
                )

        self.fields["movie"].initial = movie_id
        if info_id:
            self.fields["info"].initial = info_id

        if service_id:
            self.fields["service"].initial = service_id
        else:
            self.fields["service"].choices = chain(
                BLANK_CHOICE,
                Services.objects.all()
                .values_list("id", "name")
                .distinct()
                .order_by("name"),
            )

        self.fields["locale"].initial = "de"

        self.fields["service_movie_id"].label = mark_safe(
            "<strong>Service movie id</strong>"
        )
        self.fields["service"].label = mark_safe("<strong>Service</strong>")
        self.fields["flat"].label = mark_safe("<strong>Flat</strong>")
        self.fields["flat"].initial = self.fields["flat"]
        self.fields["flat"].choices = ((0, "0"), (1, "1"))
        self.fields["link"].label = mark_safe("<strong>Link</strong>")
        self.fields["buy_price"].label = mark_safe("<strong>Buy price</strong>")
        self.fields["rent_price"].label = mark_safe("<strong>Rent price</strong>")
        self.fields["prices"].label = mark_safe("<strong>Prices</strong>")
        self.fields["available_until"].label = mark_safe(
            "<strong>Available until</strong>"
        )
        self.fields["available_from"].label = mark_safe(
            "<strong>Available from</strong>"
        )
        self.fields["movie"].label = mark_safe("<strong>Movie</strong>")

        if self.fields["link"]:
            self.fields["link"].label = mark_safe(f"<a href={kwargs.get('instance').link}><strong>Link</strong></a>") if kwargs.get('instance') else None

    class Meta:
        model = MoviesServices
        fields = "__all__"
        exclude = ["created_at", "updated_at"]

class TransferMovieServicesForm(ActionForm):
    id_field = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_field"].label = "Info id:"

class MoviesServicesAdmin(admin.ModelAdmin):
    action_form = TransferMovieServicesForm
    ordering = ["-updated_at"]
    raw_id_fields = ["movie", "info"]
    form = MoviesServicesForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id_status",
        "movie_name",
        "service_name",
        "movies_service",
        "movie_link",
        "info_link",
        "available_from",
        "available_until",
        "updated_at",
        "value_list",
        "types_list",
        "prices_list",
        "is_active_field",
    )
    search_fields = (
        "id",
        "movie__original_title",
    )
    # list_filter = (ServiceIdFilter, #ActiveFilter,
    #               'info_id', 'movie_id')
    list_filter = ()

    readonly_fields = ("id",)

    fields = (
        "id",
        "movie",
        "info",
        "service",
        "locale",
        "service_movie_id",
        "flat",
        "link",
        "buy_price",
        "rent_price",
        "prices",
        "available_from",
        "available_until",
    )
    actions = [
        "delete_selected",
        "transfer_movieservice_to_another_info",
    ]
    def transfer_movieservice_to_another_info(self, request, queryset):
        info_id = request.POST["id_field"]
        try:
            info = Infos.objects.get(id=info_id)
        except:
            self.message_user(request, "Incorrect Info ID!", level=40)
            return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")
        
        queryset.update(
                info_id=info.id,
                movie_id=info.movie_id,
                updated_at=datetime.now().astimezone()
                )
        self.message_user(request, f"{queryset.count()} Movie services updated!", level=25)
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")
    
    transfer_movieservice_to_another_info.allow_tags = True  # type: ignore
    transfer_movieservice_to_another_info.short_description = "Transfer to another Info ID"  # type: ignore

    def get_queryset(self, request):
        service_id = request.GET.get("service_id", None)
        qs = (super().get_queryset(request)
                .select_related("movie","service","info")
                .only("id","prices","link","movie_id","info_id","service__name","service_movie_id","available_from","available_until","updated_at","info__active","movie__original_title",)
            )
        if service_id:
            return qs.filter(service_id=service_id)
        return qs

    def value_list(self, obj):
        if obj.prices:
            values_list = re.findall("HD|SD|4K", obj.prices)
            return ", ".join(values_list)
        else:
            return ""

    value_list.allow_tags = True  # type: ignore
    value_list.short_description = "value"  # type: ignore

    def types_list(self, obj):
        if obj.prices:
            values_list = re.findall("rent|buy|flat", obj.prices)
            return ", ".join(values_list)
        else:
            return ""

    types_list.allow_tags = True  # type: ignore
    types_list.short_description = "type"  # type: ignore

    def prices_list(self, obj):
        if obj.prices:
            values_list = re.findall("\d+.\d+", obj.prices)
            return ", ".join(values_list)
        else:
            return ""

    prices_list.allow_tags = True  # type: ignore
    prices_list.short_description = "price"  # type: ignore

    def is_active_field(self, obj):
        if obj.info.active:
            return True
        return False

    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def service_name(self, obj):
        return obj.service.name

    service_name.allow_tags = True  # type: ignore
    service_name.short_description = "service name"  # type: ignore

    def movies_service(self, obj):
        return format_html("<a href=%s>%s</a>" % (obj.link, obj.service_movie_id))

    movies_service.allow_tags = True  # type: ignore
    movies_service.short_description = "service movie id"  # type: ignore

    def movie_link(self, obj):
        return format_html(
            '<a href="/admin/movies/movies/%s/change">%s</a>'
            % (obj.movie_id, obj.movie_id)
        )

    movie_link.allow_tags = True  # type: ignore
    movie_link.short_description = "movie id"  # type: ignore

    def info_link(self, obj):
        return format_html(
            '<a href="/admin/movies/infos/%s/change">%s</a>'
            % (obj.info_id, obj.info_id)
        )

    info_link.allow_tags = True  # type: ignore
    info_link.short_description = "info id"  # type: ignore

    def movie_name(self, obj):
        return obj.movie.original_title

    movie_name.allow_tags = True  # type: ignore
    movie_name.short_description = "movie name"  # type: ignore


admin.site.register(Services, ServicesAdmin)
admin.site.register(SeasonServices, SeasonServicesAdmin)
admin.site.register(MoviesServices, MoviesServicesAdmin)
