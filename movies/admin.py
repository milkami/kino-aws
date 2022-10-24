import re
from datetime import datetime, timedelta
from functools import reduce
from itertools import chain
from operator import or_

import pytz
from django import forms
from django.contrib import admin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.template.defaultfilters import mark_safe
from django.utils.html import format_html

from cms.aws_helpers import delete_from_s3, upload
from cms.tmdb_helpers import fetch_movie_data, get_imdb_id, get_imdb_rating, get_tmdb_id
from distributors.models import Distributors
from genres.models import Genres
from media.models import Media, Infos

from .models import (
    AtInfosWithShowtimes,
    ChInfosWithShowtimes,
    InfoAliases,
    Infos,
    InfosWithHotShowtimes,
    InfosWithShowtimes,
    MovieAliases,
    Movies,
    MoviesPeople,
)

# Register your models here.

BLANK_CHOICE = (("", ""),)
COUNTRY_CHOICES = {
    "AW": "Aruba (AW)",
    "AF": "Afghanistan (AF)",
    "AO": "Angola (AO)",
    "AI": "Anguilla (AI)",
    "AX": "Åland Islands (AX)",
    "AL": "Albania (AL)",
    "AD": "Andorra (AD)",
    "AE": "United Arab Emirates (AE)",
    "AR": "Argentina (AR)",
    "AM": "Armenia (AM)",
    "AS": "American Samoa (AS)",
    "AQ": "Antarctica (AQ)",
    "TF": "French Southern Territories (TF)",
    "AG": "Antigua and Barbuda (AG)",
    "AU": "Australia (AU)",
    "AT": "Austria (AT)",
    "AZ": "Azerbaijan (AZ)",
    "BI": "Burundi (BI)",
    "BE": "Belgium (BE)",
    "BJ": "Benin (BJ)",
    "BQ": "Bonaire, Sint Eustatius and Saba (BQ)",
    "BF": "Burkina Faso (BF)",
    "BD": "Bangladesh (BD)",
    "BG": "Bulgaria (BG)",
    "BH": "Bahrain (BH)",
    "BS": "Bahamas (BS)",
    "BA": "Bosnia and Herzegovina (BA)",
    "BL": "Saint Barthélemy (BL)",
    "BY": "Belarus (BY)",
    "BZ": "Belize (BZ)",
    "BM": "Bermuda (BM)",
    "BO": "Bolivia, Plurinational State of (BO)",
    "BR": "Brazil (BR)",
    "BB": "Barbados (BB)",
    "BN": "Brunei Darussalam (BN)",
    "BT": "Bhutan (BT)",
    "BV": "Bouvet Island (BV)",
    "BW": "Botswana (BW)",
    "CF": "Central African Republic (CF)",
    "CA": "Canada (CA)",
    "CC": "Cocos (Keeling) Islands (CC)",
    "CH": "Switzerland (CH)",
    "CL": "Chile (CL)",
    "CN": "China (CN)",
    "CI": "Côte d'Ivoire (CI)",
    "CM": "Cameroon (CM)",
    "CD": "Congo, The Democratic Republic of the (CD)",
    "CG": "Congo (CG)",
    "CK": "Cook Islands (CK)",
    "CO": "Colombia (CO)",
    "KM": "Comoros (KM)",
    "CV": "Cabo Verde (CV)",
    "CR": "Costa Rica (CR)",
    "CU": "Cuba (CU)",
    "CW": "Curaçao (CW)",
    "CX": "Christmas Island (CX)",
    "KY": "Cayman Islands (KY)",
    "CY": "Cyprus (CY)",
    "CZ": "Czechia (CZ)",
    "DE": "Germany (DE)",
    "DJ": "Djibouti (DJ)",
    "DM": "Dominica (DM)",
    "DK": "Denmark (DK)",
    "DO": "Dominican Republic (DO)",
    "DZ": "Algeria (DZ)",
    "EC": "Ecuador (EC)",
    "EG": "Egypt (EG)",
    "ER": "Eritrea (ER)",
    "EH": "Western Sahara (EH)",
    "ES": "Spain (ES)",
    "EE": "Estonia (EE)",
    "ET": "Ethiopia (ET)",
    "FI": "Finland (FI)",
    "FJ": "Fiji (FJ)",
    "FK": "Falkland Islands (Malvinas) (FK)",
    "FR": "France (FR)",
    "FO": "Faroe Islands (FO)",
    "FM": "Micronesia, Federated States of (FM)",
    "GA": "Gabon (GA)",
    "GB": "United Kingdom (GB)",
    "GE": "Georgia (GE)",
    "GG": "Guernsey (GG)",
    "GH": "Ghana (GH)",
    "GI": "Gibraltar (GI)",
    "GN": "Guinea (GN)",
    "GP": "Guadeloupe (GP)",
    "GM": "Gambia (GM)",
    "GW": "Guinea-Bissau (GW)",
    "GQ": "Equatorial Guinea (GQ)",
    "GR": "Greece (GR)",
    "GD": "Grenada (GD)",
    "GL": "Greenland (GL)",
    "GT": "Guatemala (GT)",
    "GF": "French Guiana (GF)",
    "GU": "Guam (GU)",
    "GY": "Guyana (GY)",
    "HK": "Hong Kong (HK)",
    "HM": "Heard Island and McDonald Islands (HM)",
    "HN": "Honduras (HN)",
    "HR": "Croatia (HR)",
    "HT": "Haiti (HT)",
    "HU": "Hungary (HU)",
    "ID": "Indonesia (ID)",
    "IM": "Isle of Man (IM)",
    "IN": "India (IN)",
    "IO": "British Indian Ocean Territory (IO)",
    "IE": "Ireland (IE)",
    "IR": "Iran, Islamic Republic of (IR)",
    "IQ": "Iraq (IQ)",
    "IS": "Iceland (IS)",
    "IL": "Israel (IL)",
    "IT": "Italy (IT)",
    "JM": "Jamaica (JM)",
    "JE": "Jersey (JE)",
    "JO": "Jordan (JO)",
    "JP": "Japan (JP)",
    "KZ": "Kazakhstan (KZ)",
    "KE": "Kenya (KE)",
    "KG": "Kyrgyzstan (KG)",
    "KH": "Cambodia (KH)",
    "KI": "Kiribati (KI)",
    "KN": "Saint Kitts and Nevis (KN)",
    "KR": "Korea, Republic of (KR)",
    "KW": "Kuwait (KW)",
    "LA": "Lao People's Democratic Republic (LA)",
    "LB": "Lebanon (LB)",
    "LR": "Liberia (LR)",
    "LY": "Libya (LY)",
    "LC": "Saint Lucia (LC)",
    "LI": "Liechtenstein (LI)",
    "LK": "Sri Lanka (LK)",
    "LS": "Lesotho (LS)",
    "LT": "Lithuania (LT)",
    "LU": "Luxembourg (LU)",
    "LV": "Latvia (LV)",
    "MO": "Macao (MO)",
    "MF": "Saint Martin (French part) (MF)",
    "MA": "Morocco (MA)",
    "MC": "Monaco (MC)",
    "MD": "Moldova, Republic of (MD)",
    "MG": "Madagascar (MG)",
    "MV": "Maldives (MV)",
    "MX": "Mexico (MX)",
    "MH": "Marshall Islands (MH)",
    "MK": "North Macedonia (MK)",
    "ML": "Mali (ML)",
    "MT": "Malta (MT)",
    "MM": "Myanmar (MM)",
    "ME": "Montenegro (ME)",
    "MN": "Mongolia (MN)",
    "MP": "Northern Mariana Islands (MP)",
    "MZ": "Mozambique (MZ)",
    "MR": "Mauritania (MR)",
    "MS": "Montserrat (MS)",
    "MQ": "Martinique (MQ)",
    "MU": "Mauritius (MU)",
    "MW": "Malawi (MW)",
    "MY": "Malaysia (MY)",
    "YT": "Mayotte (YT)",
    "NA": "Namibia (NA)",
    "NC": "New Caledonia (NC)",
    "NE": "Niger (NE)",
    "NF": "Norfolk Island (NF)",
    "NG": "Nigeria (NG)",
    "NI": "Nicaragua (NI)",
    "NU": "Niue (NU)",
    "NL": "Netherlands (NL)",
    "NO": "Norway (NO)",
    "NP": "Nepal (NP)",
    "NR": "Nauru (NR)",
    "NZ": "New Zealand (NZ)",
    "OM": "Oman (OM)",
    "PK": "Pakistan (PK)",
    "PA": "Panama (PA)",
    "PN": "Pitcairn (PN)",
    "PE": "Peru (PE)",
    "PH": "Philippines (PH)",
    "PW": "Palau (PW)",
    "PG": "Papua New Guinea (PG)",
    "PL": "Poland (PL)",
    "PR": "Puerto Rico (PR)",
    "KP": "Korea, Democratic People's Republic of (KP)",
    "PT": "Portugal (PT)",
    "PY": "Paraguay (PY)",
    "PS": "Palestine, State of (PS)",
    "PF": "French Polynesia (PF)",
    "QA": "Qatar (QA)",
    "RE": "Réunion (RE)",
    "RO": "Romania (RO)",
    "RU": "Russian Federation (RU)",
    "RW": "Rwanda (RW)",
    "SA": "Saudi Arabia (SA)",
    "SD": "Sudan (SD)",
    "SN": "Senegal (SN)",
    "SG": "Singapore (SG)",
    "GS": "South Georgia and the South Sandwich Islands (GS)",
    "SH": "Saint Helena, Ascension and Tristan da Cunha (SH)",
    "SJ": "Svalbard and Jan Mayen (SJ)",
    "SB": "Solomon Islands (SB)",
    "SL": "Sierra Leone (SL)",
    "SV": "El Salvador (SV)",
    "SM": "San Marino (SM)",
    "SO": "Somalia (SO)",
    "PM": "Saint Pierre and Miquelon (PM)",
    "RS": "Serbia (RS)",
    "SS": "South Sudan (SS)",
    "ST": "Sao Tome and Principe (ST)",
    "SR": "Suriname (SR)",
    "SK": "Slovakia (SK)",
    "SI": "Slovenia (SI)",
    "SE": "Sweden (SE)",
    "SZ": "Eswatini (SZ)",
    "SX": "Sint Maarten (Dutch part) (SX)",
    "SC": "Seychelles (SC)",
    "SY": "Syrian Arab Republic (SY)",
    "TC": "Turks and Caicos Islands (TC)",
    "TD": "Chad (TD)",
    "TG": "Togo (TG)",
    "TH": "Thailand (TH)",
    "TJ": "Tajikistan (TJ)",
    "TK": "Tokelau (TK)",
    "TM": "Turkmenistan (TM)",
    "TL": "Timor-Leste (TL)",
    "TO": "Tonga (TO)",
    "TT": "Trinidad and Tobago (TT)",
    "TN": "Tunisia (TN)",
    "TR": "Turkey (TR)",
    "TV": "Tuvalu (TV)",
    "TW": "Taiwan, Province of China (TW)",
    "TZ": "Tanzania, United Republic of (TZ)",
    "UG": "Uganda (UG)",
    "UA": "Ukraine (UA)",
    "UM": "United States Minor Outlying Islands (UM)",
    "UY": "Uruguay (UY)",
    "US": "United States (US)",
    "UZ": "Uzbekistan (UZ)",
    "VA": "Holy See (Vatican City State) (VA)",
    "VC": "Saint Vincent and the Grenadines (VC)",
    "VE": "Venezuela, Bolivarian Republic of (VE)",
    "VG": "Virgin Islands, British (VG)",
    "VI": "Virgin Islands, U.S. (VI)",
    "VN": "Viet Nam (VN)",
    "VU": "Vanuatu (VU)",
    "WF": "Wallis and Futuna (WF)",
    "WS": "Samoa (WS)",
    "YE": "Yemen (YE)",
    "ZA": "South Africa (ZA)",
    "ZM": "Zambia (ZM)",
    "ZW": "Zimbabwe (ZW)",
}


class MoviesForm(forms.ModelForm):

    aliases = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 100}),
        required=False,
    )
    poster_link = forms.CharField(required=False)
    photo_link = forms.CharField(required=False)
    lock_title = forms.BooleanField(required=False)
    lock_genre = forms.BooleanField(required=False)
    lock_photo = forms.BooleanField(required=False)
    lock_poster = forms.BooleanField(required=False)
    poster_file_upload = forms.FileField()
    photo_file_upload = forms.FileField()

    infos_list = forms.CharField(required=False)
    ignore = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        genres = None
        movie_id = None
        locked_attributes = None
        imdb_id = None
        tmdb_id = None
        if kwargs.get("instance"):
            genres = kwargs.get("instance").genre
            movie_id = kwargs.get("instance").id
            imdb_id = kwargs.get("instance").imdb_id
            tmdb_id = kwargs.get("instance").tmdb_id
            locked_attributes = kwargs.get("instance").locked_attributes

        self.fields["lock_genre"].label = "Lock"
        self.fields["lock_title"].label = "Lock"
        self.fields["lock_photo"].label = "Lock"
        self.fields["lock_poster"].label = "Lock"
        # self.fields["poster_file_name"].required = False
        # self.fields["photo_file_name"].required = False
        self.fields["poster_file_upload"].required = False
        self.fields["photo_file_upload"].required = False
        self.fields["poster_file_upload"].label = mark_safe(
            "<strong>Upload poster</strong>"
        )
        self.fields["photo_file_upload"].label = mark_safe(
            "<strong>Upload photo</strong>"
        )

        infos = Infos.objects.filter(movie_id=movie_id).values_list("id", flat=True)
        infos_list = [str(i) for i in infos]
        self.fields["infos_list"].label = mark_safe("<strong>Info</strong>")
        if len(infos_list) > 1:
            self.fields["infos_list"].label = mark_safe(
                f"<a style='font-weight:bold' href='/admin/movies/infos/?movie_id={movie_id}'>Info</a>"
            )
        elif len(infos_list) == 1:
            self.fields["infos_list"].label = mark_safe(
                f"<a style='font-weight:bold' href='/admin/movies/infos/{infos_list[0]}/change'>Info</a>"
            )

        infos_list = ", ".join(infos_list)
        self.fields["infos_list"].initial = infos_list

        if locked_attributes:
            if "original_title" in locked_attributes:
                self.fields["lock_title"].initial = "on"
            if "genre" in locked_attributes:
                self.fields["lock_genre"].initial = "on"
            if "photo" in locked_attributes:
                self.fields["lock_photo"].initial = "on"
            if "poster" in locked_attributes:
                self.fields["lock_poster"].initial = "on"

        aliases_list = []
        aliases_names = MovieAliases.objects.filter(movie_id=movie_id)
        for name in aliases_names:
            if name.original_title:
                aliases_list.append(name.original_title)
        all_aliases = "\n".join(aliases_list)
        self.fields["aliases"].initial = all_aliases

        # making fields bold without being required, without extending django
        # html files:
        self.fields["original_title"].label = mark_safe(
            "<strong>Original title</strong>"
        )
        if imdb_id:
            self.fields["imdb_id"].label = mark_safe(
                '<a href="https://www.imdb.com/title/%s/">'
                "<strong>Imdb id</strong></a>" % (imdb_id)
            )
        else:
            self.fields["imdb_id"].label = mark_safe("<strong>Imdb id</strong></a>")
        self.fields["imdb_id"].required = False
        self.fields["imdb_rating"].label = mark_safe("<strong>Imdb rating</strong>")
        self.fields["premiere_date"].label = mark_safe("<strong>Premiere year</strong>")
        self.fields["original_language"].label = mark_safe(
            "<strong>Original language</strong>"
        )
        self.fields["spoken_languages"].label = mark_safe(
            "<strong>Spoken languages</strong>"
        )
        self.fields["made_in"].label = mark_safe("<strong>Made in</strong>")
        self.fields["genre"].label = mark_safe("<strong>Genre</strong>")
        if tmdb_id:
            self.fields["tmdb_id"].label = mark_safe(
                '<a href="https://www.themoviedb.org/movie/%s">'
                "<strong>Tmdb id</strong></a>" % (tmdb_id)
            )
        else:
            self.fields["tmdb_id"].label = mark_safe("<strong>Tmdb id</strong></a>")
        self.fields["tmdb_id"].required = False
        self.fields["poster_link"].label = mark_safe("<strong>Poster link</strong>")
        self.fields["photo_link"].label = mark_safe("<strong>Photo link</strong>")
        self.fields["ignore"].choices = (
            (0, "0"),
            (1, "1"),
        )
        # ______________________________________________________________

    def clean(self):
        movie_id = self.instance.id
        imdb_id = self.cleaned_data.get('imdb_id')
        tmdb_id = self.cleaned_data.get('tmdb_id')
        existing_by_imdb_id = Infos.objects.filter(active=1).filter(movie__imdb_id=imdb_id).exclude(movie__id=movie_id)
        existing_by_tmdb_id = Infos.objects.filter(active=1).filter(movie__tmdb_id=tmdb_id).exclude(movie__id=movie_id)
        if imdb_id is not None and existing_by_imdb_id.exists():
            self.add_error("imdb_id","Active movie with same IMDB id already exists.")
        if tmdb_id is not None and existing_by_tmdb_id.exists():
            self.add_error("tmdb_id", "Active movie with same TMDB id already exists.")
        return self.cleaned_data

    class Meta:
        model = Movies
        fields = "__all__"
        exclude = ["tomato_rating", "tomato_id", "metacritic_rating", "metacritic_id"]

class ActiveMoviesFilter(admin.SimpleListFilter):
    title = "Movie Status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active"),
            ("0", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(infos__active = 1)
        elif self.value() == "0":
            return queryset.filter(infos__active = 0)
        else:
            return queryset

class IgnoreMoviesFilter(admin.SimpleListFilter):
    title = "Ignore"
    parameter_name = "ignore"

    def lookups(self, request, model_admin):
        return (
            ("1", "Yes"),
            ("0", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.exclude(ignore=0)
        elif self.value() == "0":
            return queryset.filter(ignore=0)
        else:
            return queryset

class ImdbIdMoviesFilter(admin.SimpleListFilter):
    title = "IMDB id"
    parameter_name = "imdb_id"

    def lookups(self, request, model_admin):
        return (
            ("1", "With IMDB id"),
            ("0", "Without IMDB id"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.exclude(imdb_id=None)
        elif self.value() == "0":
            return queryset.filter(imdb_id=None)
        else:
            return queryset


class ImdbRatingMoviesFilter(admin.SimpleListFilter):
    title = "IMDB rating"
    parameter_name = "imdb_rating"

    def lookups(self, request, model_admin):
        return (
            ("1", "With IMDB rating"),
            ("0", "Without IMDB rating"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.exclude(imdb_rating=None).exclude(imdb_rating=0)
        elif self.value() == "0":
            return queryset.filter(imdb_rating__in=[None, 0])
        else:
            return queryset

class MediaMoviesFilter(admin.SimpleListFilter):
    title = "Media"
    parameter_name = ""

    def lookups(self, request, model_admin):
        return (
            ("1", "With Media"),
            ("0", "Without Media"),
        )

    def queryset(self, request, queryset):
        all_movie_media = Media.objects.filter(media_connection_type="Movie")
        all_movie_media = [i.media_connection_id for i in all_movie_media]
        if self.value() == "1":
            return queryset.filter(id__in = all_movie_media)
        elif self.value() == "0":
            return queryset.exclude(id__in = all_movie_media)
        else:
            return queryset

class ComingSoonMoviesFilter(admin.SimpleListFilter):
    title = "Coming soon"
    parameter_name = "comingsoon"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                infos__premiere_date__gt=datetime.today().astimezone()
            )
        if self.value() == "no":
            return queryset.filter(
                infos__premiere_date__lte=datetime.today().astimezone()
            )
        else:
            return queryset


class MoviesAdmin(admin.ModelAdmin):
    form = MoviesForm
    list_per_page = 200
    change_form_template = "admin/movies_change_form.html"
    list_display = (
        "id_status",
        "infos",
        "see_imdb_id",
        "see_tmdb_id",
        "premiere_date",
        "original_title",
        "poster",
        "photo",
        "has_imdb_rating",
        "showtimes",
        "services",
        "to_media",
        "short_created_at",
        "directors_exist",
        "actors_exist",
        "is_active_field",
    )
    search_fields = ("original_title", "imdb_id", "tmdb_id", "id")
    list_filter = (
        ActiveMoviesFilter,
        IgnoreMoviesFilter,
        ImdbIdMoviesFilter,
        ImdbRatingMoviesFilter,
        MediaMoviesFilter,
        ComingSoonMoviesFilter,
    )
    actions = [
        "add_alias",
        "delete_selected",
        "ignore_movie",
    ]

    fields = (
        "tmdb",
        "id",
        "infos_list",
        ("original_title", "lock_title"),
        "imdb_id",
        "imdb_rating",
        "tmdb_id",
        ("poster_tag", "lock_poster"),
        ("photo_tag", "lock_photo"),
        "poster_file_upload",
        "poster_link",
        "delete_poster",
        "photo_file_upload",
        "photo_link",
        "delete_photo",
        "premiere_date",
        "status",
        "original_language",
        "spoken_languages",
        "made_in",
        "add_country",
        ("genre", "lock_genre"),
        "add_genres",
        "tmdb_popularity",
        "budget",
        "revenue",
        "aliases",
        "ignore",
        "movie_services",
        "number_of_media",
        "directors_exist",
        "actors_exist",
    )
    readonly_fields = (
        "poster_tag",
        "photo_tag",
        "id",
        "tmdb",
        "movie_services",
        "delete_poster",
        "delete_photo",
        "directors_exist",
        "actors_exist",
        "add_country",
        "add_genres",
        "number_of_media",
    )

    def get_queryset(self, request):
        return  (
            super().get_queryset(request)
            .extra(
            select={"media_count":"SELECT COUNT(id) AS media_count FROM media WHERE media_connection_type='Movie' AND media_connection_id=movies.id"},
            )
            .prefetch_related("showtimes","movie_services","movie_people","movie_aliases","movie_people","infos",)
        )
    
    def to_media(self, obj):
        media_count = obj.media_count #Media.objects.filter(media_connection_type="Movie", media_connection_id=obj.id).count()
        return format_html(
            '<a href="/admin/media/media/?media_connection_type=1&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                #obj.media_count,
                media_count
            )
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def number_of_media(self, obj):
        media_count = obj.media_count #Media.objects.filter(media_connection_type="Movie", media_connection_id=obj.id).count()
        return format_html(
            '<a href="/admin/media/media/?media_connection_type=1&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                #obj.media_count,
                media_count
            )
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def add_alias(self, request, queryset):
        to_delete = []
        base_info = None
        base_movie = None
        movie_ids = queryset.values_list("id", flat=True)

        base_info = Infos.objects.filter(movie_id__in=movie_ids, active=True, locale="de").order_by("id").first()
        base_movie = base_info.movie if base_info else None

        if not (base_movie and base_info):
            base_movie = queryset.order_by("id").first()
            base_info = base_movie.infos.first()

        # for movie_id in movie_ids:
        #     info = Infos.objects.filter(movie_id=movie_id).first()
        #     if info:
        #         if info.active and info.locale == "de":
        #             base_info = info
        #             break

        # if base_info:
        #     base_movie = Movies.objects.filter(id=base_info.movie_id).first()
        # else:
        #     oldest_movie_id = min(queryset.values_list("id", flat=True))
        #     base_movie = Movies.objects.filter(id=oldest_movie_id).first()
        #     base_info = Infos.objects.filter(movie_id=oldest_movie_id).first()

        for q in queryset:
            if q.id != base_movie.id:
                alias_exist = MovieAliases.objects.filter(
                    original_title=q.rss_title, movie_id=base_movie.id
                ).first()

                if not alias_exist:
                    alias = MovieAliases(
                        movie_id=base_movie.id, original_title=q.rss_title
                    )
                    alias.save()
                to_delete.append(q)

                info = Infos.objects.filter(movie_id=q.id).first()
                if info:
                    alias_exist = InfoAliases.objects.filter(
                        title=info.rss_title, info_id=base_info.id
                    ).first()

                    if not alias_exist:
                        info_alias = InfoAliases(
                            info_id=base_info.id, title=info.rss_title
                        )
                        info_alias.save()
                    to_delete.append(info)

                    showtimes = info.showtimes.all()
                    for showtime in showtimes:
                        showtime.info_id = base_info.id
                        showtime.movie_id = base_movie.id
                        showtime.save()

                    services = info.movie_services.all()
                    for service in services:
                        service.info_id = base_info.id
                        service.movie_id = base_movie.id
                        service.save()

        for q in to_delete:
            q.delete()

        return HttpResponseRedirect(".")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def has_imdb_rating(self, obj):
        if obj.imdb_rating and obj.imdb_rating != 0:
            return "✓"
        else:
            return "✕"

    has_imdb_rating.short_description = "IMDB rating"  # type: ignore

    def movie_services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?movie_id=%s">%s</a>'
            % (obj.id, obj.movie_services.all().count())
        )

    movie_services.short_description = mark_safe("<strong>Movie services</strong>")  # type: ignore
    movie_services.allow_tags = True  # type: ignore

    def see_imdb_id(self, obj):
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>'
            % (obj.imdb_id, obj.imdb_id)
        )

    see_imdb_id.short_description = "Imdb id"  # type: ignore
    see_imdb_id.allow_tags = True  # type: ignore

    def see_tmdb_id(self, obj):
        return format_html(
            '<a href="https://www.themoviedb.org/movie/%s">%s</a>'
            % (obj.tmdb_id, obj.tmdb_id)
        )

    see_tmdb_id.short_description = "tmdb id"  # type: ignore
    see_tmdb_id.allow_tags = True  # type: ignore

    def infos(self, obj):
        return format_html(
            '<a href="/admin/movies/infos/?movie_id=%s">%s</a>'
            % (obj.id, obj.infos.count())
        )

    infos.allow_tags = True  # type: ignore
    infos.short_description = "Infos"  # type: ignore

    def id_status(self, obj):
        if obj.ignore:
            return format_html(
                '<a style="color:Grey;" href="/admin/movies/movies/%s/change/">IGNORED</a>'
                % obj.id
            )
        for info in obj.infos.all():
            if info.locale == "de" and info.premiere_date:
                if info.premiere_date.date() > datetime.today().date():
                    return format_html(
                    '<a style="color:rgb(0, 173, 36);" href="/admin/movies/movies/%s/change/">COMING SOON</a>'
                    % obj.id
                    )
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def poster(self, obj):
        all_infos = obj.infos.all()
        active_infos = [i for i in all_infos if i.active]
        if obj.poster_file_name:
            return "✓"
        else:
            return format_html('<span style="color:#c533ff">✕</span>') if active_infos else '✕'

    poster.allow_tags = True  # type: ignore
    poster.short_description = "Poster"  # type: ignore

    def photo(self, obj):
        all_infos = obj.infos.all()
        active_infos = [i for i in all_infos if i.active]
        if obj.photo_file_name:
            return "✓"
        else:
            return format_html('<span style="color:#c533ff">✕</span>') if active_infos else '✕'

    photo.allow_tags = True  # type: ignore
    photo.short_description = "Photo"  # type: ignore

    def short_created_at(self, obj):
        created_at = obj.created_at
        if created_at:
            return created_at.strftime("%B %d, %Y")

    short_created_at.allow_tags = True  # type: ignore
    short_created_at.short_description = "Created at"  # type: ignore

    def showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?movie_id=%s">%s</a>'
            % (
                obj.id,
                obj.showtimes.count(),
            )
        )

    showtimes.allow_tags = True  # type: ignore
    showtimes.short_description = "showtimes"  # type: ignore

    def directors_exist(self, obj):
        directors_present = False
        for person in obj.movie_people.all():
            if person.person_role == "director":
                directors_present = True
                break
        if directors_present:
            return "✓"
        else:
            return "✕"

    directors_exist.allow_tags = True  # type: ignore
    directors_exist.short_description = format_html("<strong>Directors</strong>")  # type: ignore

    def actors_exist(self, obj):
        actors_present = False
        for person in obj.movie_people.all():
            if person.person_role == "actor":
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"

    actors_exist.allow_tags = True  # type: ignore
    actors_exist.short_description = format_html("<strong>Actors</strong>")  # type: ignore

    def is_active_field(self, obj):
        for info in obj.infos.all():
            if info.active:
                return True
        return False

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?movie_id=%s">%s</a>'
            % (obj.id, obj.movie_services.all().count())
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "Services"  # type: ignore

    def tmdb(self, obj):
        return format_html(
            '<input type="submit" value=" Fetch Data from TMDB " ' 'name="fetching">'
        )

    tmdb.allow_tags = True  # type: ignore

    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super(MoviesAdmin, self).get_search_results(
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

    def delete_poster(self, obj):
        return format_html(
            '<input type="submit" value="Delete Poster" name="delete_poster">'
        )

    delete_poster.allow_tags = True  # type: ignore

    def delete_photo(self, obj):
        return format_html(
            '<input type="submit" value="Delete Photo" name="delete_photo">'
        )

    delete_photo.allow_tags = True  # type: ignore

    def response_change(self, request, obj):

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        lock_genre = request.POST.get("lock_genre")
        lock_photo = request.POST.get("lock_photo")
        lock_poster = request.POST.get("lock_poster")
        locked_attributes = None

        if (
            lock_title == "on"
            or lock_genre == "on"
            or lock_photo == "on"
            or lock_poster == "on"
        ):
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- original_title"
            if lock_genre == "on":
                locked_attributes += "\r\n- genre"
            if lock_photo == "on":
                locked_attributes += "\r\n- photo"
            if lock_poster == "on":
                locked_attributes += "\r\n- poster"

        obj.locked_attributes = locked_attributes
        obj.save()

        aliases_list = []
        aliases_names = MovieAliases.objects.filter(movie_id=obj.id)
        for name in aliases_names:
            aliases_list.append(name.original_title)

        current_aliases_list = request.POST.get("aliases").split("\r\n")
        to_delete = set(aliases_list) - set(current_aliases_list)
        to_create = set(current_aliases_list) - set(aliases_list)

        for alias_name in to_delete:
            for alias in MovieAliases.objects.filter(
                original_title=alias_name, movie_id=obj.id
            ):
                alias.delete()

        for alias_name in to_create:
            MovieAliases.objects.create(
                movie_id=obj.id, original_title=alias_name
            ) if alias_name else None

        # __________________________________________________________
        if "poster_file_upload" in request.FILES:
            obj.poster_file_name = request.FILES["poster_file_upload"]
            obj.save()
            upload(
                obj, request.FILES["poster_file_upload"], obj.id, "movies", "posters"
            )

        if "photo_file_upload" in request.FILES:
            obj.photo_file_name = request.FILES["photo_file_upload"]
            obj.save()
            upload(obj, request.FILES["photo_file_upload"], obj.id, "movies", "photos")

        if obj.poster_file_name == "":
            obj.poster_file_name = None
            obj.save()

        if obj.photo_file_name == "":
            obj.photo_file_name = None
            obj.save()

        if obj.imdb_id:
            get_imdb_rating(obj, obj.imdb_id)

        if obj.tmdb_id and not obj.imdb_id:
            obj.imdb_id = get_imdb_id(obj.tmdb_id, "movie")
            obj.save()

        # if obj.imdb_id and not obj.tmdb_id:
        #     obj.tmdb_id = get_tmdb_id(obj.imdb_id, "find")
        #     obj.save()

        if "fetching" in request.POST:
            message = "Nothing was done."
            message = fetch_movie_data(obj, obj.id, obj.tmdb_id)
            self.message_user(request, message)
            return HttpResponseRedirect(".")
        elif "add_genre" in request.POST:
            m = Movies.objects.get(id=obj.id)
            if not m.genre:
                m.genre = request.POST.get("genre_choices")
            else:
                m.genre += " " + request.POST.get("genre_choices")
            m.save()
            return HttpResponseRedirect(".")
        elif "delete_poster" in request.POST:
            obj.paths_to_posters = None
            obj.poster_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "movies", "posters")
            return HttpResponseRedirect(".")
        elif "delete_photo" in request.POST:
            obj.paths_to_photos = None
            obj.photo_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "movies", "photos")
            return HttpResponseRedirect(".")
        else:
            poster_url = request.POST.get("poster_link")
            photo_url = request.POST.get("photo_link")

            if poster_url:
                obj.paths_to_posters = poster_url
                obj.poster_file_name = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "movies", "posters")
            if photo_url:
                obj.paths_to_photos = photo_url
                obj.photo_file_name = photo_url
                obj.save()
                upload(obj, photo_url, obj.id, "movies", "photos")

            return super(MoviesAdmin, self).response_change(request, obj)

    def ignore_movie(self, request, queryset):
        for q in queryset:
            if q.ignore:
                q.ignore = 0
            else:
                q.ignore = 1
            q.save()
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    ignore_movie.allow_tags = True  # type: ignore
    ignore_movie.short_description = "(Un)Ignore selected"  # type: ignore

    def add_country(self, obj):
        countries = ""
        for key in COUNTRY_CHOICES:
            countries += (
                "<option value=" + key + ">" + COUNTRY_CHOICES[key] + "</option>"
            )
        return format_html(
            """<select style="margin:0" name="select_country" id="select_country">
                %s
              </select>
              <input style="margin:0;margin-top:-1px;padding:2px 10px 3px 10px;font-size:1.5em" type="button" value="+" onclick='addCountry()'>"""
            % (countries)
        )

    def add_genres(self, obj):
        genres = ""
        genre_choices = (
            Genres.objects.filter(name__isnull=False)
            .values_list("name", "name")
            .distinct()
            .order_by("name")
        )
        for genre in genre_choices:
            genres += "<option value=" + genre[0] + ">" + genre[0] + "</option>"
        return format_html(
            """<select style="margin:0" name="select_genres" id="select_genres">
                %s
              </select>
              <input style="margin:0;margin-top:-1px;padding:2px 10px 3px 10px;font-size:1.5em" type="button" value="+" onclick='addGenre()'>"""
            % (genres)
        )  # needs js from template

    add_genres.short_description = "Pick a Genre"  # type: ignore


# ____________________ INFOS ____________________


class InfosForm(forms.ModelForm):

    locale = forms.CharField(disabled=True)
    poster_link = forms.CharField(required=False)
    aliases = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 100}), required=False
    )
    lock_title = forms.BooleanField(required=False)
    lock_rating = forms.BooleanField(required=False)
    lock_summary = forms.BooleanField(required=False)
    poster_file_upload = forms.FileField()
    active = forms.ChoiceField(choices=[], required=False)
    coming_soon = forms.ChoiceField(choices=[], required=False)
    premiere_date = forms.DateField(
        widget=admin.widgets.AdminDateWidget(), required=False
    )
    movies_list = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        rating = None
        utc = pytz.UTC
        super().__init__(*args, **kwargs)

        info_id = None
        locked_attributes = None
        movie_id = None
        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "movie_id" in path:
                movie_id = re.findall("movie_id=\d+", path)
                if movie_id:
                    movie_id = movie_id[0]
                    movie_id = re.findall("\d+", movie_id)[0]
            elif "%3D" in path:
                movie_id = path.split("%3D")[-1]
        if kwargs.get("instance"):
            instance = kwargs.get("instance")
            info_id = instance.id
            locked_attributes = instance.locked_attributes
            movie_id = instance.movie.id
            rating = instance.pg_rating
            premiere_date = instance.premiere_date

        if locked_attributes:
            if "title" in locked_attributes:
                self.fields["lock_title"].initial = "on"
            if "pg_rating" in locked_attributes:
                self.fields["lock_rating"].initial = "on"
            if "summary" in locked_attributes:
                self.fields["lock_summary"].initial = "on"

        self.fields["pg_rating"].choices = (
            (0, 0),
            (6, 6),
            (12, 12),
            (16, 16),
            (18, 18),
            ("", ""),
        )
        # making fields bold without being required, without extending django
        # html files:
        movies = Movies.objects.filter(id=movie_id).values_list("id", flat=True)
        movies_list = [str(i) for i in movies]
        self.fields["movies_list"].label = mark_safe("<strong>Movie id</strong>")
        if len(movies_list) > 1:
            self.fields["movies_list"].label = mark_safe(
                f"<a style='font-weight:bold' href='/admin/movies/movies/?movie_id={movie_id}'>Movie id</a>"
            )
        elif len(movies_list) == 1:
            self.fields["movies_list"].label = mark_safe(
                f"<a style='font-weight:bold' href='/admin/movies/movies/{movies_list[0]}/change'>Movie id</a>"
            )

        movies_list = ", ".join(movies_list)
        self.fields["movies_list"].initial = movies_list

        self.fields["title"].label = mark_safe("<strong>Title</strong>")
        self.fields["distributor"].label = mark_safe("<strong>Distributor</strong>")
        self.fields["pg_rating"].label = mark_safe("<strong>Pg rating</strong>")
        self.fields["premiere_date"].label = mark_safe("<strong>Premiere date</strong>")
        self.fields["poster_file_upload"].required = False
        self.fields["poster_file_upload"].label = mark_safe(
            "<strong>Upload poster</strong>"
        )
        self.fields["locale"].required = False
        self.fields["summary"].label = mark_safe("<strong>Summary</strong>")
        self.fields["duration"].label = mark_safe("<strong>Duration</strong>")
        self.fields["active"].label = mark_safe("<strong>Active</strong>")
        self.fields["active"].initial = self.fields["active"]
        self.fields["active"].choices = ((0, "0"), (1, "1"))
        self.fields["poster_link"].label = mark_safe("<strong>Poster link</strong>")
        self.fields["coming_soon"].choices = ((1, "1"), (0, "0"))
        # _____________________________________________________________

        aliases_list = []
        aliases_names = InfoAliases.objects.filter(info_id=info_id)
        for name in aliases_names:
            if name.title:
                aliases_list.append(name.title)
        all_aliases = "\n".join(aliases_list)
        self.fields["aliases"].initial = all_aliases

        self.fields["distributor"].choices = chain(
            BLANK_CHOICE,
            Distributors.objects.all()
            .values_list("id", "name")
            .distinct()
            .order_by("name"),
        )

        # self.fields["movie"].initial = movie_id
        # self.fields["movie"].label = "Movie id"

        self.fields["pg_rating"].initial = rating if rating else ""
        self.fields["locale"].initial = "de"
        self.fields["lock_title"].label = "Lock"
        self.fields["lock_rating"].label = "Lock"
        self.fields["lock_summary"].label = "Lock"

    class Meta:
        model = Infos
        fields = "__all__"
        exclude = ["at_premiere_date", "at_coming_soon", "at_distributor_id"]


class ActiveFilter1(admin.SimpleListFilter):
    title = "Info status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active"),
            ("0", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(Q(active="1"))
        elif self.value() == "0":
            return queryset.filter(~Q(active="1"))
        else:
            return queryset


class ImdbIdFilter(admin.SimpleListFilter):
    title = "IMDB id"
    parameter_name = "imdb_id"

    def lookups(self, request, model_admin):
        return (
            ("1", "With IMDB id"),
            ("0", "Without IMDB id"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.exclude(movie__imdb_id=None)
        elif self.value() == "0":
            return queryset.filter(movie__imdb_id=None)
        else:
            return queryset


class ComingSoonInfosFilter(admin.SimpleListFilter):
    title = "Coming soon"
    parameter_name = "comingsoon"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(movie__ignore=1).filter(
                premiere_date__gt=datetime.today().astimezone()
            )
        if self.value() == "no":
            return queryset.filter(premiere_date__lte=datetime.today().astimezone())
        else:
            return queryset
      
class InfosAdmin(admin.ModelAdmin):
    # raw_id_fields = [
    #     "movie",
    # ]
    form = InfosForm
    change_form_template = "admin/info_changeform.html"
    # change_form_template = "admin/button_change_form.html"
    list_display = (
        "id_status",
        "movie_link",
        "see_imdb_id",
        "see_tmdb_id",
        "title",
        "short_premiere_date",
        "released",
        "distributor",
        "showtimes_list",
        "services",
        "to_media",
        "genre",
        "pg_rating",
        "duration",
        "directors_exist",
        "actors_exist",
        "is_active_field",
    )
    
    search_fields = (
        "title",
        "id",
        "movie__imdb_id",
        "movie__tmdb_id",
    )
    list_filter = (ActiveFilter1, ImdbIdFilter, ComingSoonInfosFilter)

    fields = (
        "id",
        # "movie",
        "movies_list",
        "locale",
        "active",
        "coming_soon",
        ("title", "lock_title"),
        "poster_tag",
        "poster_file_upload",
        "delete_poster",
        "poster_link",
        "distributor",
        ("pg_rating", "lock_rating"),
        "premiere_date",
        ("summary", "lock_summary"),
        "movie_services",
        "number_of_showtimes",
        "number_of_media",
        "duration",
        "popularity",
        "coming_soon_position",
        "tracking_id",
        "stars_count",
        "stars_average",
        "watchlist_count",
        "aliases",
    )

    readonly_fields = (
        
        "poster_tag",
        "id",
        "movie_services",
        "delete_poster",
        "number_of_showtimes",
        "number_of_media",
    )
    actions = [
        "add_alias",
        "delete_selected",
        "ignore_info",
    ]
    
    def get_queryset(self, request):
        movie_id = request.GET.get("movie_id", None)
        # qs = (super().get_queryset(request).filter(locale="de").extra(
        #     select={"media_count":"SELECT COUNT(id) AS media_count FROM media WHERE media_connection_type='Info' AND media_connection_id=infos.id"},
        #     ).order_by("-_id")
        #     .prefetch_related("showtimes","distributor","movie_services","movie__movie_people","movie"))
        qs = (
                Infos.objects.filter(locale="de")
                .prefetch_related("distributor","movie_services","movie__movie_people","movie")
                .annotate(st_count=Count("showtimes"))
                .order_by("-st_count")
             )
                
        if movie_id:
            return qs.filter(movie_id=movie_id)
        else:
            return qs

    def is_active_field(self, obj):
        if obj.active == 1:
            return True
        elif obj.active == 0:
            return False

    def add_alias(self, request, queryset):
        to_delete = []
        base_info = None
        for info in queryset:
            if info.active and info.locale == "de":
                base_info = info
                break

        if not base_info:
            info_id = min(queryset.values_list("id", flat=True))
            base_info = Infos.objects.filter(id=info_id).first()

        for q in queryset:
            if q.id != base_info.id:
                alias_exist = InfoAliases.objects.filter(
                    title=q.rss_title, info_id=base_info.id
                ).first()

                if not alias_exist:
                    alias = InfoAliases(info_id=base_info.id, title=q.rss_title)
                    alias.save()
                to_delete.append(q)

                showtimes = q.showtimes.all()
                for showtime in showtimes:
                    showtime.info_id = base_info.id
                    showtime.save()

                services = q.movie_services.all()
                for service in services:
                    service.info_id = base_info.id
                    service.save()

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(".")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def movie_services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?movie_id=%s">%s</a>'
            % (obj.movie.id, obj.movie_services.count())
        )

    movie_services.short_description = mark_safe("<strong>Movie services</strong>")  # type: ignore
    movie_services.allow_tags = True  # type: ignore

    def number_of_showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    number_of_showtimes.short_description = mark_safe("<strong>Showtimes</strong>")  # type: ignore
    number_of_showtimes.allow_tags = True  # type: ignore

    def id_status(self, obj):
        movie_ignored = obj.movie.ignore

        if movie_ignored:
            return format_html(
                '<a style="color:Grey;" href="/admin/movies/infos/%s/change/">IGNORED</a>'
                % obj.id
            )
        elif obj.premiere_date:  # check for NoneType
            if obj.premiere_date > datetime.today().astimezone():
                return format_html(
                    '<a style="color:rgb(0, 173, 36);" href="/admin/movies/infos/%s/change/">COMING SOON</a>'
                    % obj.id
                )
            else:
                return obj.id
        else:
            return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def see_imdb_id(self, obj):
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>'
            % (obj.movie.imdb_id, obj.movie.imdb_id)
        )

    see_imdb_id.short_description = "Imdb id"  # type: ignore
    see_imdb_id.allow_tags = True  # type: ignore

    def see_tmdb_id(self, obj):
        return format_html(
            '<a href="https://www.themoviedb.org/movie/%s">%s</a>'
            % (obj.movie.tmdb_id, obj.movie.tmdb_id)
        )

    see_tmdb_id.short_description = "tmdb id"  # type: ignore
    see_tmdb_id.allow_tags = True  # type: ignore

    def showtimes_list(self, obj):

        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.st_count)
        )

    showtimes_list.allow_tags = True  # type: ignore
    showtimes_list.short_description = "showtimes"  # type: ignore

    def short_premiere_date(self, obj):
        premiere_date = obj.premiere_date
        if premiere_date:
            return premiere_date.strftime("%B %d, %Y")

    short_premiere_date.allow_tags = True  # type: ignore
    short_premiere_date.short_description = "Premiere date"  # type: ignore

    def to_media(self, obj):
        media_count = Media.objects.filter(media_connection_type="Info", media_connection_id=obj.id).count()

        return format_html(
            '<a href="/admin/media/media/?media_connection_type=1&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                media_count
            )
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def number_of_media(self, obj):
        media_count = Media.objects.filter(media_connection_type="Info", media_connection_id=obj.id).count()
        return format_html(
            '<a href="/admin/media/media/?media_connection_type=1&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                media_count
            )
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def get_showtimes_count(self, obj):
        return obj.showtimes.count()

    get_showtimes_count.admin_order_field = "showtimes"  # type: ignore

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?info_id=%s">%s</a>'
            % (obj.id, obj.movie_services.count())
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "services"  # type: ignore

    def imdb_id(self, obj):
        imdb_id = obj.movie.imdb_id
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>' % (imdb_id, imdb_id)
        )

    imdb_id.short_description = "Imdb id"  # type: ignore
    imdb_id.allow_tags = True  # type: ignore

    def tmdb_id(self, obj):
        tmdb_id = obj.movie.tmdb_id
        return format_html(
            '<a href="https://www.themoviedb.org/movie/%s">%s</a>' % (tmdb_id, tmdb_id)
        )

    tmdb_id.short_description = "tmdb id"  # type: ignore
    tmdb_id.allow_tags = True  # type: ignore

    def movie_link(self, obj):
        return format_html(
            '<a href="/admin/movies/movies/%s/change">%s</a>'
            % (obj.movie_id, obj.movie_id)
        )

    movie_link.allow_tags = True  # type: ignore
    movie_link.short_description = "movie id"  # type: ignore

    def released(self, obj):
        return obj.movie.premiere_date

    released.allow_tags = True  # type: ignore
    released.short_description = "Premiere Year"  # type: ignore

    def directors_exist(self, obj):
        if obj.directors:
            return "✓"
        else:
            return "✕"

    directors_exist.allow_tags = True  # type: ignore
    directors_exist.short_description = "Directors"  # type: ignore

    def actors_exist(self, obj):
        actors_present = False
        movies_people = obj.movie.movie_people.all()
        for person in movies_people:
            if person.person_role == "actor":
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"

    actors_exist.allow_tags = True  # type: ignore
    actors_exist.short_description = "Actors"  # type: ignore

    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super().get_search_results(
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

    def delete_poster(self, obj):
        return format_html(
            '<input type="submit" value="Delete Poster" name="delete_poster">'
        )

    delete_poster.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        """
        this method is used to do things after object has been already
        made (save_model is for actions pre-first save)
        """
        poster_url = request.POST.get("poster_link")
        utc = pytz.UTC
        date_today = utc.localize(datetime.today())

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        lock_rating = request.POST.get("lock_rating")
        lock_summary = request.POST.get("lock_summary")
        locked_attributes = None

        if "_save-activate" in request.POST:
            obj.active = True
            obj.save()
            self.message_user(request, "The Info " + obj.title + " is now active")
            return HttpResponseRedirect("/admin/movies/infos/")

        # _____________________________________________________________
        if lock_title == "on" or lock_rating == "on" or lock_summary == "on":
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- title"
            if lock_rating == "on":
                locked_attributes += "\r\n- pg_rating"
            if lock_summary == "on":
                locked_attributes += "\r\n- summary"

        obj.locked_attributes = locked_attributes
        obj.save()

        # _____________________________________________________________
        if "poster_file_upload" in request.FILES:
            obj.poster_file_name = request.FILES["poster_file_upload"]
            obj.save()
            upload(obj, request.FILES["poster_file_upload"], obj.id, "infos", "posters")

        if obj.poster_file_name == "":
            obj.poster_file_name = None
            obj.save()

        aliases_list = []
        aliases_names = InfoAliases.objects.filter(info_id=obj.id)
        for name in aliases_names:
            aliases_list.append(name.title)

        current_aliases_list = request.POST.get("aliases").split("\r\n")
        to_delete = set(aliases_list) - set(current_aliases_list)
        to_create = set(current_aliases_list) - set(aliases_list)

        for alias_name in to_delete:
            for alias in InfoAliases.objects.filter(title=alias_name, info_id=obj.id):
                alias.delete()

        for alias_name in to_create:
            InfoAliases.objects.create(
                info_id=obj.id, title=alias_name
            ) if alias_name else None

        if "delete_poster" in request.POST:
            obj.paths_to_posters = None
            obj.poster_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "infos", "posters")
            return HttpResponseRedirect(".")
        else:
            if obj.premiere_date:
                if obj.premiere_date > date_today:
                    obj.coming_soon = 1
                    obj.save()
                else:
                    obj.coming_soon = 0
                    obj.save()
            if poster_url:
                obj.paths_to_posters = poster_url
                obj.poster_file_name = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "infos", "posters")

            return super(InfosAdmin, self).response_change(request, obj)

    def ignore_info(self, request, queryset):
        for q in queryset:
            m = q.movie
            if m.ignore:
                m.ignore = 0
            else:
                m.ignore = 1
            m.save()
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    ignore_info.allow_tags = True  # type: ignore
    ignore_info.short_description = "(Un)Ignore selected"  # type: ignore
    


# removed with ZBT-49
"""
class ActiveFilter2(admin.SimpleListFilter):
    title = "Info status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active with Showtimes"),
            ("0", "Inactive with Showtimes"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(Q(active="1"))
        elif self.value() == "0":
            return queryset.filter(~Q(active="1"))
        else:
            return queryset.filter(~Q(active="1"))
"""


class InfosWithShowtimesAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "movie",
    ]
    form = InfosForm
    change_form_template = "admin/button_change_form.html"

    list_display = (
        "id_status",
        "movie_link",
        "imdb_id",
        "tmdb_id",
        "title",
        "short_premiere_date",
        "released",
        "showtimes",
        "services",
        "to_media",
        "genre",
        "pg_rating",
        "duration",
        "directors_exist",
        "actors_exist",
        "is_active_field",
    )
    search_fields = ("title",)
    # list_filter = (ActiveFilter2, "coming_soon") # removed with ZBT-49

    fields = (
        "id",
        "movie",
        "locale",
        "active",
        "coming_soon",
        ("title", "lock_title"),
        "poster_tag",
        "poster_file_upload",
        "delete_poster",
        "poster_link",
        "distributor",
        ("pg_rating", "lock_rating"),
        "premiere_date",
        ("summary", "lock_summary"),
        "duration",
        "popularity",
        "coming_soon_position",
        "tracking_id",
        "stars_count",
        "stars_average",
        "watchlist_count",
        "aliases",
        "alias_choices",
        "delete_alias",
        "movie_services",
        "number_of_showtimes",
        "number_of_media",
    )

    readonly_fields = (
        "poster_tag",
        "id",
        "delete_alias",
        "movie_services",
        "delete_poster",
        "number_of_showtimes",
        "number_of_media",
    )
    actions = ["add_alias", "delete_selected", "ignore_info_with_showtime"]

    def has_add_permission(self, request, obj=None):
        return False

    def add_alias(self, request, queryset):
        to_delete = []
        base_info = None
        for info in queryset:
            if info.active and info.locale == "de":
                base_info = info
                break

        if not base_info:
            info_id = min(queryset.values_list("id", flat=True))
            base_info = Infos.objects.filter(
                id=info_id,
            ).first()

        for q in queryset:
            if q.id != base_info.id:
                alias_exist = InfoAliases.objects.filter(title=q.title).first()

                if not alias_exist:
                    alias = InfoAliases(info_id=base_info.id, title=q.title)
                    alias.save()
                to_delete.append(q)

                showtimes = q.showtimes.all()
                for showtime in showtimes:
                    showtime.info_id = base_info.id
                    showtime.save()

                services = q.movie_services.all()
                for service in services:
                    service.info_id = base_info.id
                    service.save()

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(f"./?id={base_info.id}")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def movie_services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?movie_id=%s">%s</a>'
            % (obj.movie.id, obj.movie_services.all().count())
        )

    movie_services.short_description = mark_safe("<strong>Movie services</strong>")  # type: ignore
    movie_services.allow_tags = True  # type: ignore

    def number_of_showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    number_of_showtimes.short_description = mark_safe("<strong>Showtimes</strong>")  # type: ignore
    number_of_showtimes.allow_tags = True  # type: ignore

    def number_of_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def is_active_field(self, obj):
        if obj.active == 1:
            return True
        elif obj.active == 0:
            return False

    def id_status(self, obj):
        return format_html(
            '<a href="/admin/movies/infos/%s/change/">%s</a>' % (obj.id, obj.id)
        )

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    showtimes.allow_tags = True  # type: ignore
    showtimes.short_description = "showtimes"  # type: ignore

    def short_premiere_date(self, obj):
        premiere_date = obj.premiere_date
        if premiere_date:
            return premiere_date.strftime("%B %d, %Y")

    short_premiere_date.allow_tags = True  # type: ignore
    short_premiere_date.short_description = "Premiere date"  # type: ignore

    def to_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def get_showtimes_count(self, obj):
        return obj.showtimes.count()

    get_showtimes_count.admin_order_field = "showtimes"  # type: ignore

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?info_id=%s">%s</a>'
            % (obj.id, obj.movie_services.count())
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "services"  # type: ignore

    def imdb_id(self, obj):
        imdb_id = obj.movie.imdb_id
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>' % (imdb_id, imdb_id)
        )

    imdb_id.short_description = "Imdb id"  # type: ignore
    imdb_id.allow_tags = True  # type: ignore

    def tmdb_id(self, obj):
        tmdb_id = obj.movie.tmdb_id
        return format_html(
            '<a href="https://www.themoviedb.org/movie/%s">%s</a>' % (tmdb_id, tmdb_id)
        )

    tmdb_id.short_description = "tmdb id"  # type: ignore
    tmdb_id.allow_tags = True  # type: ignore

    def movie_link(self, obj):
        return format_html(
            '<a href="/admin/movies/movies/%s/change">%s</a>'
            % (obj.movie_id, obj.movie_id)
        )

    movie_link.allow_tags = True  # type: ignore
    movie_link.short_description = "movie id"  # type: ignore

    def released(self, obj):
        return obj.movie.premiere_date

    released.allow_tags = True  # type: ignore
    released.short_description = "Premiere Year"  # type: ignore

    def directors_exist(self, obj):
        if obj.directors:
            return "✓"
        else:
            return "✕"

    directors_exist.allow_tags = True  # type: ignore
    directors_exist.short_description = "Directors"  # type: ignore

    def actors_exist(self, obj):
        actors_present = False
        movies_people = obj.movie.movie_people.all()
        for person in movies_people:
            if person.person_role == "actor":
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"

    actors_exist.allow_tags = True  # type: ignore
    actors_exist.short_description = "Actors"  # type: ignore

    def delete_alias(self, obj):
        return format_html(
            '<input type="submit" value="Delete Alias" name="delete_alias">'
        )

    delete_alias.allow_tags = True  # type: ignore

    def get_queryset(self, request):
        return (
            Infos.objects.filter(
                showtimes__info__isnull=False,
                movie__ignore=False,
                locale="de",
                showtimes__cinema__locale="de",
            )
            .filter(~Q(active="1"))
            .distinct()
            .annotate(info_id=Count("showtimes"))
            .order_by("-info_id")
        )

    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        search_words = search_term.split(",")
        if search_words:
            q_objects = [
                Q(**{field + "__icontains": word})
                for field in self.search_fields
                for word in search_words
            ]
            queryset = queryset.filter(reduce(or_, q_objects))
        return queryset, use_distinct

    def delete_poster(self, obj):
        return format_html(
            '<input type="submit" value="Delete Poster" name="delete_poster">'
        )

    delete_poster.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        """
        this method is used to do things after object has been already
        made (save_model is for actions pre-first save)
        """
        poster_url = request.POST.get("poster_link")
        utc = pytz.UTC
        date_today = utc.localize(datetime.today())

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        lock_rating = request.POST.get("lock_rating")
        lock_summary = request.POST.get("lock_summary")
        locked_attributes = None

        if lock_title == "on" or lock_rating == "on" or lock_summary == "on":
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- title"
            if lock_rating == "on":
                locked_attributes += "\r\n- pg_rating"
            if lock_summary == "on":
                locked_attributes += "\r\n- summary"

        obj.locked_attributes = locked_attributes
        obj.save()

        # _____________________________________________________________

        if "delete_alias" in request.POST:
            alias = InfoAliases.objects.filter(
                title=request.POST.get("alias_choices"), info_id=obj.id
            ).first()
            alias.delete()
            return HttpResponseRedirect(".")
        else:
            if obj.premiere_date:
                if obj.premiere_date > date_today:
                    obj.coming_soon = 1
                    obj.save()
                else:
                    obj.coming_soon = 0
                    obj.save()
            if poster_url:
                obj.paths_to_posters = poster_url
                obj.poster_file_name = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "infos", "posters")

            return super(InfosWithShowtimesAdmin, self).response_change(request, obj)

    def ignore_info_with_showtime(self, request, queryset):
        for q in queryset:
            m = q.movie
            if m.ignore:
                m.ignore = 0
            else:
                m.ignore = 1
            m.save()
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    ignore_info_with_showtime.allow_tags = True  # type: ignore
    ignore_info_with_showtime.short_description = "(Un)Ignore selected"  # type: ignore


# removed with ZBT-49
"""
class ActiveFilter3(admin.SimpleListFilter):
    title = "Info status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active with Hot Showtimes"),
            ("0", "Inactive with Hot Showtimes"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(Q(active="1"))
        elif self.value() == "0":
            return queryset.filter(~Q(active="1"))
        else:
            return queryset.filter(~Q(active="1"))
"""


class InfosWithHotShowtimesAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "movie",
    ]
    form = InfosForm
    change_form_template = "admin/button_change_form.html"

    list_display = (
        "id_status",
        "movie_link",
        "imdb_id",
        "tmdb_id",
        "title",
        "short_premiere_date",
        "released",
        "showtimes",
        "services",
        "to_media",
        "genre",
        "pg_rating",
        "duration",
        "directors_exist",
        "actors_exist",
        "is_active_field",
    )
    search_fields = ("title",)
    # list_filter = (ActiveFilter3, "coming_soon")  # removed with ZBT-49

    fields = (
        "id",
        "movie",
        "locale",
        "active",
        "coming_soon",
        ("title", "lock_title"),
        "poster_tag",
        "poster_file_upload",
        "delete_poster",
        "poster_link",
        "distributor",
        ("pg_rating", "lock_rating"),
        "premiere_date",
        ("summary", "lock_summary"),
        "duration",
        "popularity",
        "coming_soon_position",
        "tracking_id",
        "stars_count",
        "stars_average",
        "watchlist_count",
        "aliases",
        "alias_choices",
        "delete_alias",
        "movie_services",
        "number_of_showtimes",
        "number_of_media",
    )

    readonly_fields = (
        "poster_tag",
        "id",
        "delete_alias",
        "movie_services",
        "delete_poster",
        "number_of_media",
        "number_of_showtimes",
    )
    actions = [
        "add_alias",
        "delete_selected",
        "ignore_info_with_hotshowtime",
    ]
    


    def has_add_permission(self, request, obj=None):
        return False

    def add_alias(self, request, queryset):
        to_delete = []
        base_info = None
        for info in queryset:
            if info.active and info.locale == "de":
                base_info = info
                break

        if not base_info:
            info_id = min(queryset.values_list("id", flat=True))
            base_info = Infos.objects.filter(
                id=info_id,
            ).first()

        for q in queryset:
            if q.id != base_info.id:
                alias_exist = InfoAliases.objects.filter(title=q.title).first()

                if not alias_exist:
                    alias = InfoAliases(info_id=base_info.id, title=q.title)
                    alias.save()
                to_delete.append(q)

                showtimes = q.showtimes.all()
                for showtime in showtimes:
                    showtime.info_id = base_info.id
                    showtime.save()

                services = q.movie_services.all()
                for service in services:
                    service.info_id = base_info.id
                    service.save()

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(f"./?id={base_info.id}")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def movie_services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?movie_id=%s">%s</a>'
            % (obj.movie.id, obj.movie_services.all().count())
        )

    movie_services.short_description = mark_safe("<strong>Movie services</strong>")  # type: ignore
    movie_services.allow_tags = True  # type: ignore

    def number_of_showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    number_of_showtimes.short_description = mark_safe("<strong>Showtimes</strong>")  # type: ignore
    number_of_showtimes.allow_tags = True  # type: ignore

    def number_of_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def is_active_field(self, obj):
        if obj.active == 1:
            return True
        elif obj.active == 0:
            return False

    def id_status(self, obj):
        return format_html(
            '<a href="/admin/movies/infos/%s/change/">%s</a>' % (obj.id, obj.id)
        )

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    showtimes.allow_tags = True  # type: ignore
    showtimes.short_description = "showtimes"  # type: ignore

    def short_premiere_date(self, obj):
        premiere_date = obj.premiere_date
        if premiere_date:
            return premiere_date.strftime("%B %d, %Y")

    short_premiere_date.allow_tags = True  # type: ignore
    short_premiere_date.short_description = "Premiere date"  # type: ignore

    def to_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def get_showtimes_count(self, obj):
        return obj.showtimes.count()

    get_showtimes_count.admin_order_field = "showtimes"  # type: ignore

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?info_id=%s">%s</a>'
            % (obj.id, obj.movie_services.count())
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "services"  # type: ignore

    def imdb_id(self, obj):
        imdb_id = obj.movie.imdb_id
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>' % (imdb_id, imdb_id)
        )

    imdb_id.short_description = "Imdb id"  # type: ignore
    imdb_id.allow_tags = True  # type: ignore

    def tmdb_id(self, obj):
        tmdb_id = obj.movie.tmdb_id
        return format_html(
            '<a href="https://www.themoviedb.org/movie/%s">%s</a>' % (tmdb_id, tmdb_id)
        )

    tmdb_id.short_description = "tmdb id"  # type: ignore
    tmdb_id.allow_tags = True  # type: ignore

    def movie_link(self, obj):
        return format_html(
            '<a href="/admin/movies/movies/%s/change">%s</a>'
            % (obj.movie_id, obj.movie_id)
        )

    movie_link.allow_tags = True  # type: ignore
    movie_link.short_description = "movie id"  # type: ignore

    def released(self, obj):
        return obj.movie.premiere_date

    released.allow_tags = True  # type: ignore
    released.short_description = "Premiere Year"  # type: ignore

    def directors_exist(self, obj):
        if obj.directors:
            return "✓"
        else:
            return "✕"

    directors_exist.allow_tags = True  # type: ignore
    directors_exist.short_description = "Directors"  # type: ignore

    def actors_exist(self, obj):
        actors_present = False
        movies_people = MoviesPeople.objects.filter(movie_id=obj.movie_id)
        for person in movies_people:
            if person.person_role == "actor":
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"

    actors_exist.allow_tags = True  # type: ignore
    actors_exist.short_description = "Actors"  # type: ignore

    def delete_alias(self, obj):
        return format_html(
            '<input type="submit" value="Delete Alias" name="delete_alias">'
        )

    delete_alias.allow_tags = True  # type: ignore

    def get_queryset(self, request):
        utc = pytz.UTC
        yesterday = utc.localize(datetime.today() - timedelta(days=1))
        two_weeks = utc.localize(datetime.today() + timedelta(days=14))

        return (
            Infos.objects.filter(
                showtimes__info__isnull=False,
                showtimes__date__range=[yesterday, two_weeks],
                movie__ignore=False,
                locale="de",
                showtimes__cinema__locale="de",
            )
            .filter(~Q(active="1"))
            .distinct()
            .annotate(info_id=Count("showtimes"))
            .order_by("-info_id")
        )

    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        search_words = search_term.split(",")
        if search_words:
            q_objects = [
                Q(**{field + "__icontains": word})
                for field in self.search_fields
                for word in search_words
            ]
            queryset = queryset.filter(reduce(or_, q_objects))
        return queryset, use_distinct

    def delete_poster(self, obj):
        return format_html(
            '<input type="submit" value="Delete Poster" name="delete_poster">'
        )

    delete_poster.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        """
        this method is used to do things after object has been already
        made (save_model is for actions pre-first save)
        """
        poster_url = request.POST.get("poster_link")
        utc = pytz.UTC
        date_today = utc.localize(datetime.today())

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        lock_rating = request.POST.get("lock_rating")
        lock_summary = request.POST.get("lock_summary")
        locked_attributes = None

        if lock_title == "on" or lock_rating == "on" or lock_summary == "on":
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- title"
            if lock_rating == "on":
                locked_attributes += "\r\n- pg_rating"
            if lock_summary == "on":
                locked_attributes += "\r\n- summary"

        obj.locked_attributes = locked_attributes
        obj.save()

        # _____________________________________________________________

        if "delete_alias" in request.POST:
            alias = InfoAliases.objects.filter(
                title=request.POST.get("alias_choices"), info_id=obj.id
            ).first()
            alias.delete()
            return HttpResponseRedirect(".")
        else:
            if obj.premiere_date:
                if obj.premiere_date > date_today:
                    obj.coming_soon = 1
                    obj.save()
                else:
                    obj.coming_soon = 0
                    obj.save()
            if poster_url:
                obj.paths_to_posters = poster_url
                obj.poster_file_name = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "infos", "posters")

            return super(InfosWithHotShowtimesAdmin, self).response_change(request, obj)

    def ignore_info_with_hotshowtime(self, request, queryset):
        for q in queryset:
            m = q.movie
            if m.ignore:
                m.ignore = 0
            else:
                m.ignore = 1
            m.save()
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    ignore_info_with_hotshowtime.allow_tags = True  # type: ignore
    ignore_info_with_hotshowtime.short_description = "(Un)Ignore selected"  # type: ignore


# removed with ZBT-49
"""
class ActiveFilter4(admin.SimpleListFilter):
    title = "Info status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active with Showtimes"),
            ("0", "Inactive with Showtimes"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(Q(active="1"))
        elif self.value() == "0":
            return queryset.filter(~Q(active="1"))
        else:
            return queryset.filter(~Q(active="1"))
"""


class AtInfosWithShowtimesAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "movie",
    ]
    form = InfosForm
    change_form_template = "admin/button_change_form.html"

    list_display = (
        "id_status",
        "movie_link",
        "imdb_id",
        "tmdb_id",
        "title",
        "short_premiere_date",
        "released",
        "showtimes",
        "services",
        "to_media",
        "genre",
        "pg_rating",
        "duration",
        "directors_exist",
        "actors_exist",
        "is_active_field",
    )
    search_fields = ("title",)
    # list_filter = (ActiveFilter4, "coming_soon") # removed with ZBT-49

    fields = (
        "id",
        "movie",
        "locale",
        "active",
        "coming_soon",
        ("title", "lock_title"),
        "poster_tag",
        "poster_file_upload",
        "delete_poster",
        "poster_link",
        "distributor",
        ("pg_rating", "lock_rating"),
        "premiere_date",
        ("summary", "lock_summary"),
        "duration",
        "popularity",
        "coming_soon_position",
        "tracking_id",
        "stars_count",
        "stars_average",
        "watchlist_count",
        "aliases",
        # "alias_choices",
        # "delete_alias",
        "movie_services",
        "number_of_showtimes",
        "number_of_media",
    )

    readonly_fields = (
        "poster_tag",
        "id",
        # "delete_alias",
        "movie_services",
        "delete_poster",
        "number_of_showtimes",
        "number_of_media",
    )
    actions = ["add_alias", "delete_selected", "ignore_info_with_showtime"]

    def has_add_permission(self, request, obj=None):
        return False

    def add_alias(self, request, queryset):
        to_delete = []
        base_info = None
        for info in queryset:
            if info.active and info.locale == "de":
                base_info = info
                break

        if not base_info:
            info_id = min(queryset.values_list("id", flat=True))
            base_info = Infos.objects.filter(
                id=info_id,
            ).first()

        for q in queryset:
            if q.id != base_info.id:
                alias_exist = InfoAliases.objects.filter(title=q.title).first()

                if not alias_exist:
                    alias = InfoAliases(info_id=base_info.id, title=q.title)
                    alias.save()
                to_delete.append(q)

                showtimes = q.showtimes.all()
                for showtime in showtimes:
                    showtime.info_id = base_info.id
                    showtime.save()

                services = q.movie_services.all()
                for service in services:
                    service.info_id = base_info.id
                    service.save()

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(f"./?id={base_info.id}")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def movie_services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?movie_id=%s">%s</a>'
            % (obj.movie.id, obj.movie_services.all().count())
        )

    movie_services.short_description = mark_safe("<strong>Movie services</strong>")  # type: ignore
    movie_services.allow_tags = True  # type: ignore

    def number_of_showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    number_of_showtimes.short_description = mark_safe("<strong>Showtimes</strong>")  # type: ignore
    number_of_showtimes.allow_tags = True  # type: ignore

    def number_of_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def is_active_field(self, obj):
        if obj.active == 1:
            return True
        elif obj.active == 0:
            return False

    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    showtimes.allow_tags = True  # type: ignore
    showtimes.short_description = "showtimes"  # type: ignore

    def short_premiere_date(self, obj):
        premiere_date = obj.premiere_date
        if premiere_date:
            return premiere_date.strftime("%B %d, %Y")

    short_premiere_date.allow_tags = True  # type: ignore
    short_premiere_date.short_description = "Premiere date"  # type: ignore

    def to_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def get_showtimes_count(self, obj):
        return obj.showtimes.count()

    get_showtimes_count.admin_order_field = "showtimes"  # type: ignore

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?info_id=%s">%s</a>'
            % (obj.id, obj.movie_services.count())
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "services"  # type: ignore

    def imdb_id(self, obj):
        imdb_id = obj.movie.imdb_id
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>' % (imdb_id, imdb_id)
        )

    imdb_id.short_description = "Imdb id"  # type: ignore
    imdb_id.allow_tags = True  # type: ignore

    def tmdb_id(self, obj):
        tmdb_id = obj.movie.tmdb_id
        return format_html(
            '<a href="https://www.themoviedb.org/movie/%s">%s</a>' % (tmdb_id, tmdb_id)
        )

    tmdb_id.short_description = "tmdb id"  # type: ignore
    tmdb_id.allow_tags = True  # type: ignore

    def movie_link(self, obj):
        return format_html(
            '<a href="/admin/movies/movies/%s/change">%s</a>'
            % (obj.movie_id, obj.movie_id)
        )

    movie_link.allow_tags = True  # type: ignore
    movie_link.short_description = "movie id"  # type: ignore

    def released(self, obj):
        return obj.movie.premiere_date

    released.allow_tags = True  # type: ignore
    released.short_description = "Premiere Year"  # type: ignore

    def directors_exist(self, obj):
        if obj.directors:
            return "✓"
        else:
            return "✕"

    directors_exist.allow_tags = True  # type: ignore
    directors_exist.short_description = "Directors"  # type: ignore

    def actors_exist(self, obj):
        actors_present = False
        movies_people = MoviesPeople.objects.filter(movie_id=obj.movie_id)
        for person in movies_people:
            if person.person_role == "actor":
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"

    actors_exist.allow_tags = True  # type: ignore
    actors_exist.short_description = "Actors"  # type: ignore

    # def delete_alias(self, obj):
    #     return format_html(
    #         '<input type="submit" value="Delete Alias" name="delete_alias">'
    #     )

    # delete_alias.allow_tags = True  # type: ignore

    def get_queryset(self, request):
        return (
            Infos.objects.filter(
                showtimes__info__isnull=False,
                movie__ignore=False,
                locale="de",
                showtimes__cinema__locale="at",
            )
            .filter(~Q(active="1"))
            .distinct()
            .annotate(info_id=Count("showtimes"))
            .order_by("-info_id")
        )

    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        search_words = search_term.split(",")
        if search_words:
            q_objects = [
                Q(**{field + "__icontains": word})
                for field in self.search_fields
                for word in search_words
            ]
            queryset = queryset.filter(reduce(or_, q_objects))
        return queryset, use_distinct

    def delete_poster(self, obj):
        return format_html(
            '<input type="submit" value="Delete Poster" name="delete_poster">'
        )

    delete_poster.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        """
        this method is used to do things after object has been already
        made (save_model is for actions pre-first save)
        """
        poster_url = request.POST.get("poster_link")
        utc = pytz.UTC
        date_today = utc.localize(datetime.today())

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        lock_rating = request.POST.get("lock_rating")
        lock_summary = request.POST.get("lock_summary")
        locked_attributes = None

        if lock_title == "on" or lock_rating == "on" or lock_summary == "on":
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- title"
            if lock_rating == "on":
                locked_attributes += "\r\n- pg_rating"
            if lock_summary == "on":
                locked_attributes += "\r\n- summary"

        obj.locked_attributes = locked_attributes
        obj.save()

        # _____________________________________________________________

        if "poster_file_upload" in request.FILES:
            obj.poster_file_name = request.FILES["poster_file_upload"]
            obj.save()
            upload(obj, request.FILES["poster_file_upload"], obj.id, "infos", "posters")

        if obj.poster_file_name == "":
            obj.poster_file_name = None
            obj.save()

        aliases_list = []
        aliases_names = InfoAliases.objects.filter(info_id=obj.id)
        for name in aliases_names:
            aliases_list.append(name.title)

        current_aliases_list = request.POST.get("aliases").split("\r\n")
        to_delete = set(aliases_list) - set(current_aliases_list)
        to_create = set(current_aliases_list) - set(aliases_list)

        for alias_name in to_delete:
            for alias in InfoAliases.objects.filter(title=alias_name, info_id=obj.id):
                alias.delete()

        for alias_name in to_create:
            InfoAliases.objects.create(
                info_id=obj.id, title=alias_name
            ) if alias_name else None
        
        if "delete_poster" in request.POST:
            obj.paths_to_posters = None
            obj.poster_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "infos", "posters")
            return HttpResponseRedirect(".")
        else:
            if obj.premiere_date:
                if obj.premiere_date > date_today:
                    obj.coming_soon = 1
                    obj.save()
                else:
                    obj.coming_soon = 0
                    obj.save()
            if poster_url:
                obj.paths_to_posters = poster_url
                obj.poster_file_name = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "infos", "posters")

            return super(AtInfosWithShowtimesAdmin, self).response_change(request, obj)

    def ignore_info_with_showtime(self, request, queryset):
        for q in queryset:
            m = q.movie
            if m.ignore:
                m.ignore = 0
            else:
                m.ignore = 1
            m.save()
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    ignore_info_with_showtime.allow_tags = True  # type: ignore
    ignore_info_with_showtime.short_description = "(Un)Ignore selected"  # type: ignore


# removed with ZBT-49
"""
class ActiveFilter5(admin.SimpleListFilter):
    title = "Info status"
    parameter_name = "active"

    def lookups(self, request, model_admin):
        return (
            ("1", "Active with Showtimes"),
            ("0", "Inactive with Showtimes"),
        )

    def queryset(self, request, queryset):
        if self.value() == "1":
            return queryset.filter(Q(active="1"))
        elif self.value() == "0":
            return queryset.filter(~Q(active="1"))
        else:
            return queryset.filter(~Q(active="1"))
"""


class ChInfosWithShowtimesAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "movie",
    ]
    form = InfosForm
    change_form_template = "admin/button_change_form.html"

    list_display = (
        "id_status",
        "movie_link",
        "imdb_id",
        "tmdb_id",
        "title",
        "short_premiere_date",
        "released",
        "showtimes",
        "services",
        "to_media",
        "genre",
        "pg_rating",
        "duration",
        "directors_exist",
        "actors_exist",
        "is_active_field",
    )
    search_fields = ("title",)
    # list_filter = (ActiveFilter5, "coming_soon") # removed with ZBT-49

    fields = (
        "id",
        "movie",
        "locale",
        "active",
        "coming_soon",
        ("title", "lock_title"),
        "poster_tag",
        "poster_file_upload",
        "delete_poster",
        "poster_link",
        "distributor",
        ("pg_rating", "lock_rating"),
        "premiere_date",
        ("summary", "lock_summary"),
        "duration",
        "popularity",
        "coming_soon_position",
        "tracking_id",
        "stars_count",
        "stars_average",
        "watchlist_count",
        "aliases",
        # "alias_choices",
        # "delete_alias",
        "movie_services",
        "number_of_showtimes",
        "number_of_media",
    )

    readonly_fields = (
        "poster_tag",
        "id",
        # "delete_alias",
        "movie_services",
        "delete_poster",
        "number_of_showtimes",
        "number_of_media",
    )
    actions = ["add_alias", "delete_selected", "ignore_info_with_showtime"]

    def has_add_permission(self, request, obj=None):
        return False

    def add_alias(self, request, queryset):
        to_delete = []
        base_info = None
        for info in queryset:
            if info.active and info.locale == "de":
                base_info = info
                break

        if not base_info:
            info_id = min(queryset.values_list("id", flat=True))
            base_info = Infos.objects.filter(
                id=info_id,
            ).first()

        for q in queryset:
            if q.id != base_info.id:
                alias_exist = InfoAliases.objects.filter(title=q.title).first()

                if not alias_exist:
                    alias = InfoAliases(info_id=base_info.id, title=q.title)
                    alias.save()
                to_delete.append(q)

                showtimes = q.showtimes.all()
                for showtime in showtimes:
                    showtime.info_id = base_info.id
                    showtime.save()

                services = q.movie_services.all()
                for service in services:
                    service.info_id = base_info.id
                    service.save()

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(f"./?id={base_info.id}")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def movie_services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?movie_id=%s">%s</a>'
            % (obj.movie.id, obj.movie_services.all().count())
        )

    movie_services.short_description = mark_safe("<strong>Movie services</strong>")  # type: ignore
    movie_services.allow_tags = True  # type: ignore

    def number_of_showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    number_of_showtimes.short_description = mark_safe("<strong>Showtimes</strong>")  # type: ignore
    number_of_showtimes.allow_tags = True  # type: ignore

    def number_of_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def is_active_field(self, obj):
        if obj.active == 1:
            return True
        elif obj.active == 0:
            return False

    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def showtimes(self, obj):
        return format_html(
            '<a href="/admin/cinemas/showtimes/?info_id=%s">%s</a>'
            % (obj.id, obj.showtimes.count())
        )

    showtimes.allow_tags = True  # type: ignore
    showtimes.short_description = "showtimes"  # type: ignore

    def short_premiere_date(self, obj):
        premiere_date = obj.premiere_date
        if premiere_date:
            return premiere_date.strftime("%B %d, %Y")

    short_premiere_date.allow_tags = True  # type: ignore
    short_premiere_date.short_description = "Premiere date"  # type: ignore

    def to_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
            % (obj.id, Media.objects.filter(media_connection_id=obj.id).count())
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def get_showtimes_count(self, obj):
        return obj.showtimes.count()

    get_showtimes_count.admin_order_field = "showtimes"  # type: ignore

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/moviesservices/?info_id=%s">%s</a>'
            % (obj.id, obj.movie_services.count())
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "services"  # type: ignore

    def imdb_id(self, obj):
        imdb_id = obj.movie.imdb_id
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>' % (imdb_id, imdb_id)
        )

    imdb_id.short_description = "Imdb id"  # type: ignore
    imdb_id.allow_tags = True  # type: ignore

    def tmdb_id(self, obj):
        tmdb_id = obj.movie.tmdb_id
        return format_html(
            '<a href="https://www.themoviedb.org/movie/%s">%s</a>' % (tmdb_id, tmdb_id)
        )

    tmdb_id.short_description = "tmdb id"  # type: ignore
    tmdb_id.allow_tags = True  # type: ignore

    def movie_link(self, obj):
        return format_html(
            '<a href="/admin/movies/movies/%s/change">%s</a>'
            % (obj.movie_id, obj.movie_id)
        )

    movie_link.allow_tags = True  # type: ignore
    movie_link.short_description = "movie id"  # type: ignore

    def released(self, obj):
        return obj.movie.premiere_date

    released.allow_tags = True  # type: ignore
    released.short_description = "Premiere Year"  # type: ignore

    def directors_exist(self, obj):
        if obj.directors:
            return "✓"
        else:
            return "✕"

    directors_exist.allow_tags = True  # type: ignore
    directors_exist.short_description = "Directors"  # type: ignore

    def actors_exist(self, obj):
        actors_present = False
        movies_people = MoviesPeople.objects.filter(movie_id=obj.movie_id)
        for person in movies_people:
            if person.person_role == "actor":
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"

    actors_exist.allow_tags = True  # type: ignore
    actors_exist.short_description = "Actors"  # type: ignore

    # def delete_alias(self, obj):
    #     return format_html(
    #         '<input type="submit" value="Delete Alias" name="delete_alias">'
    #     )

    # delete_alias.allow_tags = True  # type: ignore

    def get_queryset(self, request):
        return (
            Infos.objects.filter(
                showtimes__info__isnull=False,
                movie__ignore=False,
                locale="de",
                showtimes__cinema__locale="ch",
            )
            .filter(~Q(active="1"))
            .distinct()
            .annotate(info_id=Count("showtimes"))
            .order_by("-info_id")
        )

    def get_search_results(self, request, queryset, search_term):
        queryset2, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        search_words = search_term.split(",")
        if search_words:
            q_objects = [
                Q(**{field + "__icontains": word})
                for field in self.search_fields
                for word in search_words
            ]
            queryset = queryset.filter(reduce(or_, q_objects))
        return queryset, use_distinct

    def delete_poster(self, obj):
        return format_html(
            '<input type="submit" value="Delete Poster" name="delete_poster">'
        )

    delete_poster.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        """
        this method is used to do things after object has been already
        made (save_model is for actions pre-first save)
        """
        poster_url = request.POST.get("poster_link")
        utc = pytz.UTC
        date_today = utc.localize(datetime.today())

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        lock_rating = request.POST.get("lock_rating")
        lock_summary = request.POST.get("lock_summary")
        locked_attributes = None

        if lock_title == "on" or lock_rating == "on" or lock_summary == "on":
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- title"
            if lock_rating == "on":
                locked_attributes += "\r\n- pg_rating"
            if lock_summary == "on":
                locked_attributes += "\r\n- summary"

        obj.locked_attributes = locked_attributes
        obj.save()

        # _____________________________________________________________

        if "poster_file_upload" in request.FILES:
            obj.poster_file_name = request.FILES["poster_file_upload"]
            obj.save()
            upload(obj, request.FILES["poster_file_upload"], obj.id, "infos", "posters")

        if obj.poster_file_name == "":
            obj.poster_file_name = None
            obj.save()

        aliases_list = []
        aliases_names = InfoAliases.objects.filter(info_id=obj.id)
        for name in aliases_names:
            aliases_list.append(name.title)

        current_aliases_list = request.POST.get("aliases").split("\r\n")
        to_delete = set(aliases_list) - set(current_aliases_list)
        to_create = set(current_aliases_list) - set(aliases_list)

        for alias_name in to_delete:
            for alias in InfoAliases.objects.filter(title=alias_name, info_id=obj.id):
                alias.delete()

        for alias_name in to_create:
            InfoAliases.objects.create(
                info_id=obj.id, title=alias_name
            ) if alias_name else None
        
        if "delete_poster" in request.POST:
            obj.paths_to_posters = None
            obj.poster_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "infos", "posters")
            return HttpResponseRedirect(".")
        else:
            if obj.premiere_date:
                if obj.premiere_date > date_today:
                    obj.coming_soon = 1
                    obj.save()
                else:
                    obj.coming_soon = 0
                    obj.save()
            if poster_url:
                obj.paths_to_posters = poster_url
                obj.poster_file_name = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "infos", "posters")

            return super(ChInfosWithShowtimesAdmin, self).response_change(request, obj)

    def ignore_info_with_showtime(self, request, queryset):
        for q in queryset:
            m = q.movie
            if m.ignore:
                m.ignore = 0
            else:
                m.ignore = 1
            m.save()
        return HttpResponseRedirect(f"./?{request.get_full_path().split('?')[-1]}")

    ignore_info_with_showtime.allow_tags = True  # type: ignore
    ignore_info_with_showtime.short_description = "(Un)Ignore selected"  # type: ignore


admin.site.register(Movies, MoviesAdmin)
admin.site.register(Infos, InfosAdmin)
admin.site.register(InfosWithShowtimes, InfosWithShowtimesAdmin)
admin.site.register(InfosWithHotShowtimes, InfosWithHotShowtimesAdmin)
admin.site.register(AtInfosWithShowtimes, AtInfosWithShowtimesAdmin)
admin.site.register(ChInfosWithShowtimes, ChInfosWithShowtimesAdmin)
