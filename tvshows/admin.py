import re
from functools import reduce
from operator import or_

from django import forms
from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.defaultfilters import mark_safe
from django.utils.html import format_html

from cms.aws_helpers import delete_from_s3, upload
from cms.tmdb_helpers import (
    fetch_seasons_and_episodes,
    fetch_tvshow_data,
    get_imdb_id,
    get_imdb_rating,
    get_tmdb_id,
)
from genres.models import Genres
from media.models import Media
from services.models import SeasonServices

from .models import (
    Episodes,
    EpisodeTranslations,
    Seasons,
    SeasonTranslations,
    TvShowAliases,
    TvShowPeople,
    TvShows,
    TvShowTranslationAliases,
    TvShowTranslations,
)

# Register your models here.

BLANK_CHOICE = (("", ""),)

ALIAS_CHOICES = []  # type: ignore

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


class TvShowsForm(forms.ModelForm):

    aliases = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 100}), required=False
    )
    poster_link = forms.CharField(required=False)
    photo_link = forms.CharField(required=False)
    lock_title = forms.BooleanField(required=False)
    lock_photo = forms.BooleanField(required=False)
    lock_poster = forms.BooleanField(required=False)
    poster_file_upload = forms.FileField()
    photo_file_upload = forms.FileField()

    translations_list = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tvshow_id = None
        locked_attributes = None
        imdb_id = None
        tmdb_id = None
        if kwargs.get("instance"):
            tvshow_id = kwargs.get("instance").id
            imdb_id = kwargs.get("instance").imdb_id
            tmdb_id = kwargs.get("instance").tmdb_id
            locked_attributes = kwargs.get("instance").locked_attributes

        self.fields["lock_title"].label = "Lock"
        if locked_attributes:
            if "original_title" in locked_attributes:
                self.fields["lock_title"].initial = "on"
            if "photo" in locked_attributes:
                self.fields["lock_photo"].initial = "on"
            if "poster" in locked_attributes:
                self.fields["lock_poster"].initial = "on"

        self.fields["translations_list"].label = mark_safe(
            "<strong>Tv show translation</strong>"
        )
        translations = TvShowTranslations.objects.filter(
            tv_show_id=tvshow_id
        ).values_list("id", flat=True)
        translations_list = [str(i) for i in translations]
        if len(translations_list) > 1:
            self.fields["translations_list"].label = mark_safe(
                f"<a style='font-weight:bold' href='/admin/tvshows/tvshowtranslations"
                f"/?tv_show_id={tvshow_id}'>Tv show translation</a>"
            )
        elif len(translations_list) == 1:
            self.fields["translations_list"].label = mark_safe(
                f"<a style='font-weight:bold' href='/admin/tvshows/tvshowtranslations"
                f"/{translations_list[0]}/change'>Tv show translation</a>"
            )

        translations_list = ", ".join(translations_list)
        self.fields["translations_list"].initial = translations_list

        aliases_list = []
        aliases_names = TvShowAliases.objects.filter(tv_show_id=tvshow_id)
        for name in aliases_names:
            if name.original_title:
                aliases_list.append(name.original_title)

        all_aliases = "\n".join(aliases_list)
        self.fields["aliases"].initial = all_aliases

        self.fields["poster_file_upload"].required = False
        self.fields["photo_file_upload"].required = False
        self.fields["poster_file_upload"].label = mark_safe(
            "<strong>Upload poster</strong>"
        )
        self.fields["photo_file_upload"].label = mark_safe(
            "<strong>Upload photo</strong>"
        )

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
        self.fields["imdb_rating"].label = mark_safe("<strong>Imdb rating</strong>")
        if tmdb_id:
            self.fields["tmdb_id"].label = mark_safe(
                '<a href="https://www.themoviedb.org/tv/%s">'
                "<strong>Tmdb id</strong></a>" % (tmdb_id)
            )
        else:
            self.fields["tmdb_id"].label = mark_safe("<strong>Tmdb id</strong></a>")
        self.fields["genre"].label = mark_safe("<strong>Genre</strong>")
        self.fields["made_in"].label = mark_safe("<strong>Made in</strong>")
        self.fields["original_language"].label = mark_safe(
            "<strong>Original languages</strong>"
        )
        self.fields["languages"].label = mark_safe("<strong>Languages</strong>")
        self.fields["poster_link"].label = mark_safe("<strong>Poster link</strong>")
        self.fields["photo_link"].label = mark_safe("<strong>Photo link</strong>")
        # _____________________________________________________________

    def clean(self):
        tvshow_id = self.instance.id
        imdb_id = self.cleaned_data.get('imdb_id')
        tmdb_id = self.cleaned_data.get('tmdb_id')
        existing_by_imdb_id = TvShowTranslations.objects.filter(active=1).filter(tv_show__imdb_id=imdb_id).exclude(tv_show__id=tvshow_id)
        existing_by_tmdb_id = TvShowTranslations.objects.filter(active=1).filter(tv_show__tmdb_id=tmdb_id).exclude(tv_show__id=tvshow_id)
        if imdb_id is not None and existing_by_imdb_id.exists():
            self.add_error("imdb_id","Active TV Show with same IMDB id already exists.")
        if tmdb_id is not None and existing_by_tmdb_id.exists():
            self.add_error("tmdb_id", "Active TV Show with same TMDB id already exists.")

    class Meta:
        model = TvShows
        fields = "__all__"


class TvShowAdmin(admin.ModelAdmin):
    list_per_page = 200
    form = TvShowsForm
    # change_form_template = "admin/fetch_tmdb_change_form.html"
    change_form_template = "admin/tvshows_change_form.html"
    list_display = (
        "id_status",
        "translations",
        "see_imdb_id",
        "see_tmdb_id",
        "first_air_date",
        "original_title",
        "poster",
        "photo",
        "has_imdb_rating",
        "created_at",
        "to_media",
        "services",
        "seasons",
        "episodes",
        "directors_exist",
        "actors_exist",
        "is_active_field",
    )
    search_fields = ("id", "original_title", "imdb_id", "tmdb_id")
    readonly_fields = (
        "poster_tag",
        "photo_tag",
        "id",
        "add_genres",
        "tmdb",
        "seasons_list",
        "delete_poster",
        "delete_photo",
        "directors_exist",
        "actors_exist",
        "add_country",
        "get_episodes",
        "number_of_media",
    )
    actions = [
        "add_alias",
        "delete_selected",
    ]

    fields = (
        "tmdb",
        "id",
        "translations_list",
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
        "status",
        "in_production",
        "original_language",
        "languages",
        "made_in",
        "add_country",
        "genre",
        "add_genres",
        "tmdb_popularity",
        "episode_run_time",
        "number_of_episodes",
        "number_of_seasons",
        "homepage",
        "first_air_date",
        "last_air_date",
        "networks",
        "type",
        "aliases",
        "seasons_list",
        "get_episodes",
        "directors_exist",
        "actors_exist",
        "number_of_media",
    )

    def get_queryset(self,request):
        return (TvShows.objects
        .prefetch_related("tv_show_translations","season_services","seasons","tv_show_people","seasons__episodes")
        .extra(select={"media_count":"SELECT COUNT(id) AS media_count FROM media WHERE media_connection_type='TvShow' AND media_connection_id=tv_shows.id"})
        
        )

    def add_alias(self, request, queryset):
        to_delete = []
        base_tvshow = None
        base_translation = None

        tvshow_ids = queryset.values_list("id", flat=True)
        for tvshow_id in tvshow_ids:
            translation = TvShowTranslations.objects.filter(
                tv_show_id=tvshow_id
            ).first()
            if translation:
                if translation.active and translation.locale == "de":
                    base_translation = translation
                    break

        if base_translation:
            base_tvshow = TvShows.objects.filter(id=base_translation.tv_show_id).first()
        else:
            oldest_tvshow_id = min(queryset.values_list("id", flat=True))
            base_tvshow = TvShows.objects.filter(id=oldest_tvshow_id).first()
            base_translation = TvShowTranslations.objects.filter(
                tv_show_id=oldest_tvshow_id
            ).first()

        for q in queryset:
            if q.id != base_tvshow.id:
                alias_exist = TvShowAliases.objects.filter(
                    original_title=q.original_title
                ).first()

                if not alias_exist:
                    alias = TvShowAliases(
                        tv_show_id=base_tvshow.id, original_title=q.original_title
                    )
                    alias.save()
                to_delete.append(q)

                translation = TvShowTranslations.objects.filter(tv_show_id=q.id).first()
                if translation:
                    alias_exist = TvShowTranslationAliases.objects.filter(
                        title=translation.title
                    ).first()

                    if not alias_exist:
                        translation_alias = TvShowTranslationAliases(
                            tv_show_translation_id=base_translation.id,
                            title=translation.title,
                        )
                        translation_alias.save()
                    to_delete.append(translation)

                    services = translation.season_services.all()
                    for service in services:
                        season = Seasons.objects.filter(
                            tv_show_id=base_tvshow.id,
                            season_number=service.season_number,
                        ).first()
                        if season:
                            service.tv_show_translation_id = base_translation.id
                            service.tv_show_id = base_tvshow.id
                            service.season_id = season.id
                            service.season_translation_id = (
                                season.season_translations.first().id
                            )
                            service.save()

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(f"./?id={base_tvshow.id}")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def to_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_type=0&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                obj.media_count,
            )
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def number_of_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_type=0&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                obj.media_count,
            )
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def is_active_field(self, obj):
        active = False
        translations = obj.tv_show_translations.all()
        for translation in translations:
            if translation.active:
                active = True
                break
        return active

    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/seasonservices/?tv_show_id=%s">%s</a>'
            % (obj.id, obj.season_services.count())
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "Services"  # type: ignore

    def seasons_list(self, obj):
        seasons = obj.seasons.all().order_by("season_number")

        return format_html(
            "<br>".join(
                f'Season <a href="/admin/tvshows/seasons/{s.id}">{s.season_number}</a>:'
                f' <a href="/admin/tvshows/episodes/?season_id={s.id}">{s.episodes.count()}</a>&nbsp;&nbsp;&nbsp;'
                f'(Services: <a style="color:grey" href="/admin/services/seasonservices/?season_id={s.id}">'
                f"{s.season_services.count(): <4}</a>)"
                for s in seasons
            )
        )

    seasons_list.allow_tags = True  # type: ignore
    seasons_list.short_description = mark_safe("<strong>Season num + Episodes</strong>")  # type: ignore

    def translations(self, obj):
        return format_html(
            '<a href="/admin/tvshows/tvshowtranslations/?tv_show_id=%s">%s</a>'
            % (obj.id, obj.tv_show_translations.all().count())
        )

    translations.allow_tags = True  # type: ignore
    translations.short_description = "Translations"  # type: ignore

    def poster(self, obj):
        all_translations = obj.tv_show_translations.all()
        active_translations = [i for i in all_translations if i.active]
        if obj.poster_file_name:
            return "✓"
        else:
             return format_html('<span style="color:#c533ff">✕</span>') if active_translations else '✕'

    poster.allow_tags = True  # type: ignore
    poster.short_description = "Poster"  # type: ignore

    def photo(self, obj):
        all_translations = obj.tv_show_translations.all()
        active_translations = [i for i in all_translations if i.active]
        if obj.photo_file_name:
            return "✓"
        else:
            return format_html('<span style="color:#c533ff">✕</span>') if active_translations else '✕'

    photo.allow_tags = True  # type: ignore
    photo.short_description = "Photo"  # type: ignore

    def see_imdb_id(self, obj):
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>'
            % (obj.imdb_id, obj.imdb_id)
        )

    see_imdb_id.short_description = "Imdb id"  # type: ignore
    see_imdb_id.allow_tags = True  # type: ignore

    def see_tmdb_id(self, obj):
        return format_html(
            '<a href="https://www.themoviedb.org/tv/%s">%s</a>'
            % (obj.tmdb_id, obj.tmdb_id)
        )

    see_tmdb_id.short_description = "tmdb id"  # type: ignore
    see_tmdb_id.allow_tags = True  # type: ignore

    def tmdb(self, obj):
        return format_html(
            '<input type="submit" value=" Fetch Data from TMDB " name="fetching">'
        )

    def seasons(self, obj):
        seasons = obj.seasons.count()
        return format_html(
            '<a href="/admin/tvshows/seasons/?tv_show_id=%s">%s</a>' % (obj.id, seasons)
        )

    seasons.allow_tags = True  # type: ignore
    seasons.short_description = "seasons"  # type: ignore

    def episodes(self, obj):
        episode_count = 0
        seasons = obj.seasons.all()
        for season in seasons:
            episode_count += season.episodes.count()

        return format_html(
            '<a href="/admin/tvshows/episodes/?tv_show_id=%s">%s</a>'
            % (obj.id, episode_count)
        )

    episodes.allow_tags = True  # type: ignore
    episodes.short_description = "episodes"  # type: ignore

    def directors_exist(self, obj):
        directors_present = False
        tv_show_people = obj.tv_show_people.all()
        for person in tv_show_people:
            if person.person_role == "creator":
                directors_present = True
                break

        if directors_present:
            return "✓"
        else:
            return "✕"

    directors_exist.allow_tags = True  # type: ignore
    directors_exist.short_description = format_html("<strong>Creators</strong>")  # type: ignore

    def actors_exist(self, obj):
        actors_present = False
        tv_show_people = obj.tv_show_people.all()
        for person in tv_show_people:
            if person.person_role == "actor":
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"

    actors_exist.allow_tags = True  # type: ignore
    actors_exist.short_description = format_html("<strong>Actors</strong>")  # type: ignore

    def get_episodes(self, obj):
        return format_html(
            '<input type="submit" value="Get episodes" name="get_episodes">'
        )

    get_episodes.allow_tags = True  # type: ignore

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

    def delete_photo(self, obj):
        return format_html(
            '<input type="submit" value="Delete Photo" name="delete_photo">'
        )

    delete_photo.allow_tags = True  # type: ignore

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
            """
            <select style="margin:0" name="select_genres" id="select_genres">
                %s
              </select>
              <input style="margin:0;margin-top:-1px;padding:2px 10px 3px 10px;font-size:1.5em" type="button" value="+" onclick='addGenre()'>"""
            % (genres)
        )

    add_genres.short_description = "Pick a genre"  # type: ignore

    def has_imdb_rating(self, obj):
        if obj.imdb_rating:
            return "✓"
        else:
            return "✕"

    has_imdb_rating.short_description = "IMDB rating"  # type: ignore

    def response_change(self, request, obj):

        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        lock_photo = request.POST.get("lock_photo")
        lock_poster = request.POST.get("lock_poster")
        locked_attributes = None

        if lock_title == "on" or lock_photo == "on" or lock_poster == "on":
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- original_title"
            if lock_photo == "on":
                locked_attributes += "\r\n- photo"
            if lock_poster == "on":
                locked_attributes += "\r\n- poster"

        obj.locked_attributes = locked_attributes
        obj.save()

        # __________________________________________________________

        if "poster_file_upload" in request.FILES:
            obj.poster_file_name = request.FILES["poster_file_upload"]
            obj.save()
            upload(
                obj, request.FILES["poster_file_upload"], obj.id, "tv_shows", "posters"
            )

        if "photo_file_upload" in request.FILES:
            obj.photo_file_name = request.FILES["photo_file_upload"]
            obj.save()
            upload(
                obj, request.FILES["photo_file_upload"], obj.id, "tv_shows", "photos"
            )

        if obj.poster_file_name == "":
            obj.poster_file_name = None
            obj.save()

        if obj.photo_file_name == "":
            obj.photo_file_name = None
            obj.save()

        if obj.imdb_id:
            get_imdb_rating(obj, obj.imdb_id)

        if obj.tmdb_id and not obj.imdb_id:
            obj.imdb_id = get_imdb_id(obj.tmdb_id, "tv")
            obj.save()

        if obj.imdb_id and not obj.tmdb_id:
            obj.tmdb_id = get_tmdb_id(obj.imdb_id, "find")
            obj.save()

        aliases_list = []
        aliases_names = TvShowAliases.objects.filter(tv_show_id=obj.id)
        for name in aliases_names:
            aliases_list.append(name.original_title)

        current_aliases_list = request.POST.get("aliases").split("\r\n")
        to_delete = set(aliases_list) - set(current_aliases_list)
        to_create = set(current_aliases_list) - set(aliases_list)

        for alias_name in to_delete:
            for alias in TvShowAliases.objects.filter(
                original_title=alias_name, tv_show_id=obj.id
            ):
                alias.delete()

        for alias_name in to_create:
            TvShowAliases.objects.create(
                tv_show_id=obj.id, original_title=alias_name
            ) if alias_name else None

        if "fetching" in request.POST:
            message = "Nothing was done."
            message = fetch_tvshow_data(obj, obj.id, obj.tmdb_id)
            self.message_user(request, message)
            return HttpResponseRedirect(".")
        elif "delete_poster" in request.POST:
            obj.poster_path = None
            obj.poster_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "tv_shows", "posters")
            return HttpResponseRedirect(".")
        elif "delete_photo" in request.POST:
            obj.photo_path = None
            obj.photo_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "tv_shows", "photos")
            return HttpResponseRedirect(".")
        elif "get_episodes" in request.POST:
            message = "Nothing was done."
            message = fetch_seasons_and_episodes(obj, obj.id, obj.tmdb_id)
            self.message_user(request, message)
            return HttpResponseRedirect(".")
        else:
            poster_url = request.POST.get("poster_link")
            photo_url = request.POST.get("photo_link")
            if poster_url:
                obj.poster_path = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "tv_shows", "posters")
            if photo_url:
                obj.photo_path = photo_url
                obj.save()
                upload(obj, photo_url, obj.id, "tv_shows", "photos")
            return super(TvShowAdmin, self).response_change(request, obj)


# ____________________ TVSHOW TRANSLATIONS ____________________


class TvShowTranslationsForm(forms.ModelForm):
    active = forms.ChoiceField(choices=[], required=False)
    locale = forms.CharField(disabled=True)
    poster_link = forms.CharField(required=False)
    aliases = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 100}), required=False
    )
    lock_title = forms.BooleanField(required=False)

    poster_file_upload = forms.FileField()

    def __init__(self, *args, **kwargs):
        rating = None
        super().__init__(*args, **kwargs)

        translation_id = None
        locked_attributes = None
        tv_show_id = None
        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "tv_show_id" in path:
                tv_show_id = re.findall("tv_show_id=\d+", path)
                if tv_show_id:
                    tv_show_id = tv_show_id[0]
                    tv_show_id = re.findall("\d+", tv_show_id)[0]
            elif "%3D" in path:
                tv_show_id = path.split("%3D")[-1]

        if kwargs.get("instance"):
            instance = kwargs.get("instance")
            translation_id = instance.id
            locked_attributes = instance.locked_attributes
            tv_show_id = instance.tv_show.id

        self.fields["lock_title"].label = "Lock"
        if locked_attributes:
            if "title" in locked_attributes:
                self.fields["lock_title"].initial = "on"

        self.fields["pg_rating"].choices = (
            (0, 0),
            (6, 6),
            (12, 12),
            (16, 16),
            (18, 18),
            ("", ""),
        )
        self.fields["poster_file_upload"].required = False
        self.fields["poster_file_upload"].label = mark_safe(
            "<strong>Upload poster</strong>"
        )

        # making fields bold without being required, without extending django
        # html files:
        self.fields["title"].label = mark_safe("<strong>Title</strong>")
        self.fields["summary"].label = mark_safe("<strong>Summary</strong>")
        self.fields["pg_rating"].label = mark_safe("<strong>Pg rating</strong>")
        self.fields["active"].label = mark_safe("<strong>Active</strong>")
        self.fields["poster_link"].label = mark_safe("<strong>Poster link</strong>")
        # _____________________________________________________________

        aliases_list = []
        aliases_names = TvShowTranslationAliases.objects.filter(
            tv_show_translation_id=translation_id
        )
        for name in aliases_names:
            if name.title:
                aliases_list.append(name.title)

        all_aliases = "\n".join(aliases_list)
        self.fields["aliases"].initial = all_aliases

        self.fields["locale"].initial = "de"
        if kwargs.get("instance"):
            rating = kwargs.get("instance").pg_rating
        self.fields["pg_rating"].initial = rating if rating else ""

        self.fields["tv_show"].initial = tv_show_id
        self.fields["tv_show"].label = "Tv show id"
        self.fields["active"].label = mark_safe("<strong>Active</strong>")
        self.fields["active"].initial = self.fields["active"]
        self.fields["active"].choices = ((0, "0"), (1, "1"))

    class Meta:
        model = TvShowTranslations
        fields = "__all__"


class ActiveFilter(admin.SimpleListFilter):
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


class TvShowTranslationAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "tv_show",
    ]
    form = TvShowTranslationsForm
    change_form_template = "admin/tvshowtranslation_changeform.html"
    # change_form_template = "admin/button_change_form.html"
    list_display = (
        "id_status",
        "tv_show_link",
        "title",
        "original_title",
        "pg_rating",
        "genre",
        "imdb_id",
        "tmdb_id",
        "to_media",
        "summary_exists",
        "photo",
        "poster",
        "to_media",
        "services",
        "seasons",
        "episodes",
        "is_active_field",
    )
    search_fields = (
        "id",
        "title",
    )
    list_filter = (ActiveFilter,)  # 'tv_show_id',)
    readonly_fields = (
        "poster_tag",
        "id",
        "seasons_list",
        "delete_poster",
        "number_of_media",
    )

    fields = (
        "id",
        "tv_show",
        "locale",
        "active",
        ("title", "lock_title"),
        "poster_tag",
        "poster_file_upload",
        "poster_link",
        "delete_poster",
        "pg_rating",
        "summary",
        "popularity",
        "stars_count",
        "stars_average",
        "watchlist_count",
        "aliases",
        "seasons_list",
        "number_of_media",
    )
    actions = [
        "add_alias",
        "delete_selected",
    ]

    def get_queryset(self,request):
        return (TvShowTranslations.objects.prefetch_related("tv_show","season_services","tv_show__seasons","tv_show__seasons__episodes")
        .extra(select={"media_count":"SELECT COUNT(id) AS media_count FROM media WHERE media_connection_type='TvShowTranslation' AND media_connection_id=tv_show_translations.id"}))

    def add_alias(self, request, queryset):
        to_delete = []
        base_translation = None
        for translation in queryset:
            if translation.active and translation.locale == "de":
                base_translation = translation
                break

        if not base_translation:
            oldest_translation_id = min(queryset.values_list("id", flat=True))
            base_translation = TvShowTranslations.objects.filter(
                id=oldest_translation_id
            ).first()

        for q in queryset:
            if q.id != base_translation.id:
                alias_exist = TvShowTranslationAliases.objects.filter(
                    title=q.title
                ).first()

                if not alias_exist:
                    alias = TvShowTranslationAliases(
                        tv_show_translation_id=base_translation.id, title=q.title
                    )
                    alias.save()
                to_delete.append(q)

                services = q.season_services.all()
                for service in services:
                    service.tv_show_translation_id = base_translation.id
                    service.save()

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(f"./?id={base_translation.id}")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def seasons_list(self, obj):
        seasons = obj.tv_show.seasons.order_by("season_number")
        return format_html(
            "<br>".join(
                f'Season <a href="/admin/tvshows/seasons/{s.id}">{s.season_number}</a>:'
                f' <a href="/admin/tvshows/episodes/?season_id={s.id}">{s.episodes.count()}</a>&nbsp;&nbsp;&nbsp;'
                f'(Services: <a style="color:grey" href="/admin/services/seasonservices/?season_id={s.id}">'
                f"{s.season_services.count(): <4}</a>)"
                for s in seasons
            )
        )

    seasons_list.allow_tags = True  # type: ignore
    seasons_list.short_description = mark_safe("<strong>Season num + Episodes</strong>")  # type: ignore

    def seasons(self, obj):
        seasons = obj.tv_show.seasons.count()
        return format_html(
            '<a href="/admin/tvshows/seasons/?tv_show_id=%s">%s</a>'
            % (obj.tv_show_id, seasons)
        )

    seasons.allow_tags = True  # type: ignore
    seasons.short_description = "seasons"  # type: ignore

    def episodes(self, obj):
        episode_count = 0
        seasons = obj.tv_show.seasons.all()
        for season in seasons:
            episode_count += season.episodes.count()

        return format_html(
            '<a href="/admin/tvshows/episodes/?tv_show_id=%s">%s</a>'
            % (obj.tv_show_id, episode_count)
        )

    episodes.allow_tags = True  # type: ignore
    episodes.short_description = "episodes"  # type: ignore

    def is_active_field(self, obj):
        if obj.active == 1:
            return True
        elif obj.active == 0:
            return False

    def id_status(self, obj):
        return obj.id

    id_status.allow_tags = True  # type: ignore
    id_status.short_description = "ID"  # type: ignore

    def original_title(self, obj):
        return obj.tv_show.original_title

    original_title.allow_tags = True  # type: ignore
    original_title.short_description = "Orginial Title"  # type: ignore

    def tv_show_link(self, obj):
        return format_html(
            '<a href="/admin/tvshows/tvshows/%s/change">%s</a>'
            % (obj.tv_show_id, obj.tv_show_id)
        )

    tv_show_link.allow_tags = True  # type: ignore
    tv_show_link.short_description = "tv_show_id"  # type: ignore

    def to_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_type=0&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                obj.media_count,
            )
        )

    to_media.allow_tags = True  # type: ignore
    to_media.short_description = "Media"  # type: ignore

    def number_of_media(self, obj):
        return format_html(
            '<a href="/admin/media/media/?media_connection_type=0&media_connection_id=%s">%s</a>'
            % (
                obj.id,
                Media.objects.filter(media_connection_type="TvShowTranslation")
                .filter(media_connection_id=obj.id)
                .count(),
            )
        )

    number_of_media.short_description = mark_safe("<strong>Media</strong>")  # type: ignore
    number_of_media.allow_tags = True  # type: ignore

    def genre(self, obj):
        return obj.tv_show.genre

    genre.allow_tags = True  # type: ignore
    genre.short_description = "genre"  # type: ignore

    def imdb_id(self, obj):
        imdb_id = obj.tv_show.imdb_id
        return format_html(
            '<a href="https://www.imdb.com/title/%s/">%s</a>' % (imdb_id, imdb_id)
        )

    imdb_id.short_description = "Imdb id"  # type: ignore
    imdb_id.allow_tags = True  # type: ignore

    def tmdb_id(self, obj):
        tmdb_id =obj.tv_show.tmdb_id
        return format_html(
            '<a href="https://www.themoviedb.org/tv/%s">%s</a>' % (tmdb_id, tmdb_id)
        )

    tmdb_id.short_description = "tmdb id"  # type: ignore
    tmdb_id.allow_tags = True  # type: ignore

    def summary_exists(self, obj):
        if obj.summary:
            return "✓"
        else:
            return "✕"

    summary_exists.allow_tags = True  # type: ignore
    summary_exists.short_description = "summary"  # type: ignore

    def photo(self, obj):
        if obj.tv_show.photo_file_name:
            return "✓"
        else:
            return "✕"

    photo.allow_tags = True  # type: ignore
    photo.short_description = "photo"  # type: ignore

    def poster(self, obj):
        if obj.tv_show.poster_file_name:
            return "✓"
        else:
            return "✕"

    poster.allow_tags = True  # type: ignore
    poster.short_description = "poster"  # type: ignore

    def services(self, obj):
        return format_html(
            '<a href="/admin/services/seasonservices/'
            '?tv_show_translation_id=%s">%s</a>'
            % (
                obj.id,
                obj.season_services.count(),
            )
        )

    services.allow_tags = True  # type: ignore
    services.short_description = "services"  # type: ignore

    """def creators_exist(self, obj):
        if obj.directors:
            return "✓"
        else:
            return "✕"
    directors_exist.allow_tags = True
    directors_exist.short_description = 'Directors'

    def actors_exist(self, obj):
        actors_present = False
        for person in MoviesPeople.objects.filter(movie_id=obj.movie_id):
            if person.person_role == 'actor':
                actors_present = True
                break

        if actors_present:
            return "✓"
        else:
            return "✕"
    actors_exist.allow_tags = True
    actors_exist.short_description = 'Actors'"""

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
        #### LOCKED ATTRIBUTES ####
        ## format example: #---\r\n- title\r\n- pg_rating\r\n- at_premiere_date

        lock_title = request.POST.get("lock_title")
        locked_attributes = None

        if lock_title == "on":
            locked_attributes = "---"
            if lock_title == "on":
                locked_attributes += "\r\n- title"

        obj.locked_attributes = locked_attributes
        obj.save()

        # ____________Save and activate______________________________

        if "_save-activate" in request.POST:
            obj.active = True
            obj.save()
            self.message_user(
                request, "The Tv Show Translation " + obj.title + " is now active"
            )
            return HttpResponseRedirect("/admin/tvshows/tvshowtranslations/")

        # __________________________________________________________

        if "poster_file_upload" in request.FILES:
            obj.poster_file_name = request.FILES["poster_file_upload"]
            obj.save()
            upload(
                obj,
                request.FILES["poster_file_upload"],
                obj.id,
                "tv_show_translation",
                "posters",
            )

        if obj.poster_file_name == "":
            obj.poster_file_name = None
            obj.save()

        aliases_list = []
        aliases_names = TvShowTranslationAliases.objects.filter(
            tv_show_translation_id=obj.id
        )
        for name in aliases_names:
            aliases_list.append(name.title)

        current_aliases_list = request.POST.get("aliases").split("\r\n")
        to_delete = set(aliases_list) - set(current_aliases_list)
        to_create = set(current_aliases_list) - set(aliases_list)

        for alias_name in to_delete:
            for alias in TvShowTranslationAliases.objects.filter(
                title=alias_name, tv_show_translation_id=obj.id
            ):
                alias.delete()

        for alias_name in to_create:
            TvShowTranslationAliases.objects.create(
                tv_show_translation_id=obj.id, title=alias_name
            ) if alias_name else None

        if "delete_poster" in request.POST:
            obj.poster_path = None
            obj.poster_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "tv_show_translation", "posters")
            return HttpResponseRedirect(".")
        else:
            poster_url = request.POST.get("poster_link")
            if poster_url:
                obj.poster_path = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "tv_show_translation", "posters")
            return super(TvShowTranslationAdmin, self).response_change(request, obj)


# ____________________ SEASONS ____________________


class SeasonsForm(forms.ModelForm):
    poster_file_upload = forms.FileField()
    poster_link = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        rating = None
        super().__init__(*args, **kwargs)

        tv_show_id = None
        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "tv_show_id" in path:
                tv_show_id = re.findall("tv_show_id=\d+", path)
                if tv_show_id:
                    tv_show_id = tv_show_id[0]
                    tv_show_id = re.findall("\d+", tv_show_id)[0]
            elif "%3D" in path:
                tv_show_id = path.split("%3D")[-1]
        if kwargs.get("instance"):
            instance = kwargs.get("instance")
            tv_show_id = instance.tv_show.id

        self.fields["poster_file_upload"].required = False
        self.fields["poster_file_upload"].label = mark_safe(
            "<strong>Upload poster</strong>"
        )

        self.fields["tmdb_id"].label = mark_safe("<strong>Tmdb id</strong>")
        self.fields["tv_show"].label = mark_safe("<strong>Tv show id</strong>")
        self.fields["season_number"].label = mark_safe("<strong>Season number</strong>")
        self.fields["poster_link"].label = mark_safe("<strong>Poster link</strong>")

        # _____________________________________________________________

        self.fields["tv_show"].initial = tv_show_id
        self.fields["tv_show"].label = "Tv show id"

    class Meta:
        model = Seasons
        fields = "__all__"
        exclude = [
            "created_at",
            "updated_at",
        ]


class SeasonAdmin(admin.ModelAdmin):
    ordering = ["season_number"]
    raw_id_fields = [
        "tv_show",
    ]
    form = SeasonsForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "short_season_number",
        "poster",
        "see_tmdb_id",
        "air_date",
        "title",
        "translations",
        "episodes",
        "season_services",
    )

    readonly_fields = (
        "id",
        "delete_poster",
    )

    fields = (
        "id",
        "tmdb_id",
        "tv_show",
        "air_date",
        "season_number",
        "poster_file_upload",
        "poster_link",
        "delete_poster",
    )
    search_fields = (
        "id",
        "tv_show__imdb_id",
        "tv_show__tmdb_id",
        "tv_show__id",
        "tmdb_id",
        "tv_show__original_title",
        "tv_show__tv_show_translations__title",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tv_show","tv_show__tv_show_translations","season_services","season_translations","episodes")

    def short_season_number(self, obj):
        return obj.season_number

    short_season_number.admin_order_field = "season_number"  # type: ignore
    short_season_number.short_description = "#"  # type: ignore

    def see_tmdb_id(self, obj):
        return format_html(
            '<a href="https://www.themoviedb.org/tv/%s/season/%s">%s</a>'
            % (
                obj.tv_show.tmdb_id,
                obj.season_number,
                obj.tv_show.tmdb_id,
            )
        )

    see_tmdb_id.short_description = "tmdb id"  # type: ignore
    see_tmdb_id.allow_tags = True  # type: ignore

    def poster(self, obj):
        return (
            format_html(
                '<img src="{}" style="max-width: 125px;"/>'.format(
                    f"https://s3-eu-west-1.amazonaws.com/kinode/production/"
                    f"seasons/posters/{obj.id}/tiny.jpg"
                )
            )
            if obj.poster_file_name
            else "-"
        )

    poster.allow_tags = True  # type: ignore
    poster.short_description = "poster"  # type: ignore

    def title(self, obj):
        season_translation = obj.season_translations.all()
        return season_translation[0].title if season_translation else "-"
        

    title.allow_tags = True  # type: ignore
    title.short_description = "title"  # type: ignore

    def translations(self, obj):
        return obj.season_translations.count()

    translations.allow_tags = True  # type: ignore
    translations.short_description = "translations"  # type: ignore

    # def media_list(self, obj):
    #     return format_html(
    #         '<a href="/admin/media/media/?media_connection_id=%s">%s</a>'
    #         % (obj.id, obj.media_count)
    #     )

    # media_list.allow_tags = True  # type: ignore
    # media_list.short_description = "media"  # type: ignore

    def season_services(self, obj):
        season_services = obj.season_services.count()
        return format_html(
            '<a href="/admin/services/seasonservices/?season_id=%s">%s</a>'
            % (obj.id, season_services)
        )

    season_services.allow_tags = True  # type: ignore
    season_services.short_description = "season_services"  # type: ignore

    def episodes(self, obj):
        episodes = obj.episodes.count()
        return format_html(
            '<a href="/admin/tvshows/episodes/?season_id=%s">%s</a>'
            % (obj.id, episodes)
        )

    episodes.allow_tags = True  # type: ignore
    episodes.short_description = "episodes"  # type: ignore

    def delete_poster(self, obj):
        return format_html(
            '<input type="submit" value="Delete Poster" name="delete_poster">'
        )

    delete_poster.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        if "poster_file_upload" in request.FILES:
            obj.poster_file_name = request.FILES["poster_file_upload"]
            obj.save()
            upload(
                obj, request.FILES["poster_file_upload"], obj.id, "seasons", "posters"
            )

        if obj.poster_file_name == "":
            obj.poster_file_name = None
            obj.save()

        if "delete_poster" in request.POST:
            obj.poster_path = None
            obj.poster_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "seasons", "posters")
            return HttpResponseRedirect(".")
        else:
            poster_url = request.POST.get("poster_link")

            if poster_url:
                obj.poster_path = poster_url
                obj.save()
                upload(obj, poster_url, obj.id, "seasons", "posters")

            return super(SeasonAdmin, self).response_change(request, obj)


# ____________________ EPISODES ____________________


class EpisodesForm(forms.ModelForm):
    photo_file_upload = forms.FileField()
    photo_link = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        rating = None
        super().__init__(*args, **kwargs)

        season_id = None
        tv_show_id = None
        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "season_id" in path:
                season_id = re.findall("season_id=\d+", path)
                if season_id:
                    season_id = season_id[0]
                    season_id = re.findall("\d+", season_id)[0]
            elif "%3D" in path:
                season_id = path.split("%3D")[-1]

            season = Seasons.objects.filter(id=season_id).first()
            if season:
                tv_show_id = season.tv_show.id
        if kwargs.get("instance"):
            instance = kwargs.get("instance")
            tv_show_id = instance.season.id

        self.fields["original_title"].label = mark_safe(
            "<strong>Original title</strong>"
        )
        self.fields["tv_show"].label = mark_safe("<strong>Tv show id</strong>")
        self.fields["season"].label = mark_safe("<strong>Season id</strong>")
        self.fields["season_number"].label = mark_safe("<strong>Season number</strong>")
        self.fields["episode_number"].label = mark_safe(
            "<strong>Episode number</strong>"
        )
        self.fields["air_date"].label = mark_safe("<strong>Air date</strong>")
        self.fields["tmdb_id"].label = mark_safe("<strong>Tmdb id</strong>")
        self.fields["imdb_id"].label = mark_safe("<strong>Imdb id</strong>")
        self.fields["imdb_rating"].label = mark_safe("<strong>Imdb rating</strong>")
        self.fields["photo_file_upload"].required = False
        self.fields["photo_file_upload"].label = mark_safe(
            "<strong>Upload photo</strong>"
        )
        self.fields["photo_link"].label = mark_safe("<strong>Photo link</strong>")

        # _____________________________________________________________

        self.fields["season"].initial = season_id
        self.fields["tv_show"].initial = tv_show_id
        self.fields["season"].label = "Season id"
        self.fields["tv_show"].label = "Tv show id"

    class Meta:
        model = Seasons
        fields = "__all__"
        exclude = [
            "created_at",
            "updated_at",
        ]


class EpisodeAdmin(admin.ModelAdmin):
    ordering = ["episode_number"]
    raw_id_fields = ["tv_show", "season"]
    form = EpisodesForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "short_episode_number",
        "poster",
        "see_tmdb_id",
        "air_date",
        "en_title",
        "de_title",
        "summary",
        "translations",
        "imdb_id",
        "imdb_rating",
    )

    readonly_fields = (
        "id",
        "delete_photo",
    )

    fields = (
        "id",
        "original_title",
        "tv_show",
        "season",
        "season_number",
        "air_date",
        "tmdb_id",
        "episode_number",
        "imdb_id",
        "imdb_rating",
        "photo_file_upload",
        "photo_link",
        "delete_photo",
    )

    def get_queryset(self, request):
        return (super().get_queryset(request).select_related("tv_show","season").prefetch_related("episode_translations")
            .only("tv_show__tmdb_id","season__season_number","episode_number","photo_file_name","original_title","air_date","imdb_id","imdb_rating")
        )

    def short_episode_number(self, obj):
        episode_num = obj.episode_number
        return episode_num if episode_num else "-"

    short_episode_number.short_description = "#"  # type: ignore
    short_episode_number.admin_order_field = "episode_number"  # type: ignore

    def see_tmdb_id(self, obj):
        return format_html(
            '<a href="https://www.themoviedb.org/tv/%s/season/%s/episode/%s">%s</a>'
            % (
                obj.tv_show.tmdb_id,
                obj.season.season_number,
                obj.episode_number,
                obj.tv_show.tmdb_id,
            )
        )

    see_tmdb_id.short_description = "tmdb id"  # type: ignore
    see_tmdb_id.allow_tags = True  # type: ignore

    def poster(self, obj):
        return (
            format_html(
                '<img src="{}" style="max-width: 175px;"/>'.format(
                    f"https://s3-eu-west-1.amazonaws.com/kinode/production/"
                    f"episodes/photos/{obj.id}/tiny.jpg"
                )
            )
            if obj.photo_file_name
            else "-"
        )

    poster.allow_tags = True  # type: ignore
    poster.short_description = "poster"  # type: ignore

    def summary(self, obj):
        episode_translation = obj.episode_translations.all()

        if episode_translation:
            if episode_translation[0].summary:
                return "✓"
        
        return "✕"

    summary.allow_tags = True  # type: ignore
    summary.short_description = "summary"  # type: ignore

    def en_title(self, obj):
        return obj.original_title

    en_title.allow_tags = True  # type: ignore
    en_title.short_description = "en title"  # type: ignore

    def de_title(self, obj):
        de_title = obj.episode_translations.all()
        
        return de_title[0].title if de_title else "-"

    de_title.allow_tags = True  # type: ignore
    de_title.short_description = "de title"  # type: ignore

    def translations(self, obj):
        return obj.episode_translations.count()

    translations.allow_tags = True  # type: ignore
    translations.short_description = "translations"  # type: ignore

    def delete_photo(self, obj):
        return format_html(
            '<input type="submit" value="Delete Photo" name="delete_photo">'
        )

    delete_photo.allow_tags = True  # type: ignore

    def response_change(self, request, obj):
        if "photo_file_upload" in request.FILES:
            obj.photo_file_name = request.FILES["photo_file_upload"]
            obj.save()
            upload(
                obj, request.FILES["photo_file_upload"], obj.id, "episodes", "photos"
            )

        if obj.photo_file_name == "":
            obj.photo_file_name = None
            obj.save()

        if "delete_photo" in request.POST:
            obj.photo_path = None
            obj.photo_file_name = None
            obj.save()
            delete_from_s3(obj, obj.id, "episodes", "photos")
            return HttpResponseRedirect(".")
        else:
            photo_url = request.POST.get("photo_link")

            if photo_url:
                obj.photo_path = photo_url
                obj.save()
                upload(obj, photo_url, obj.id, "episodes", "photos")

            return super(EpisodeAdmin, self).response_change(request, obj)


admin.site.register(TvShows, TvShowAdmin)
admin.site.register(TvShowTranslations, TvShowTranslationAdmin)
admin.site.register(Seasons, SeasonAdmin)
admin.site.register(Episodes, EpisodeAdmin)
