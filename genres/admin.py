from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html

from .models import GenreAliases, Genres
from django.db.models import Count

# Register your models here.


class GenreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Genres
        fields = "__all__"
        exclude = ["created_at", "updated_at"]


class GenresAdmin(admin.ModelAdmin):
    form = GenreForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "name",
        "aliases",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "id",
        "name",
    )
    actions = [
        "add_alias",
        "delete_selected",
    ]
    def get_queryset(self, request):
        return (super().get_queryset(request)
        .annotate(Count("genre_aliases"))
        )

    def add_alias(self, request, queryset):
        genre_id = min(queryset.values_list("id", flat=True))
        to_delete = []
        for q in queryset:
            if q.id != genre_id:
                alias = GenreAliases(genre_id=genre_id, name=q.name)
                alias.save()
                to_delete.append(q)

        for q in to_delete:
            q.delete()
        return HttpResponseRedirect(".")

    add_alias.allow_tags = True  # type: ignore
    add_alias.short_description = "Convert to Alias"  # type: ignore

    def aliases(self, obj):
        return format_html(
            '<a href="/admin/genres/genrealiases/?genre_id=%s">%s</a>'
            % (obj.id, 
            obj.genre_aliases__count
            )
        )

    aliases.allow_tags = True  # type: ignore
    aliases.short_description = "Aliases"  # type: ignore


class GenreIdFilter(admin.SimpleListFilter):
    title = "Genre Id"
    parameter_name = "genre_id"

    def lookups(self, request, model_admin):
        genres = set([c for c in Genres.objects.all()])
        return [(c.id, f"{c.id} ({c.name})") for c in genres]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(id=self.value())
        else:
            return queryset


class GenreAliasesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = GenreAliases
        fields = "__all__"
        exclude = ["created_at", "updated_at"]


class GenreAliasesAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "genre",
    ]
    form = GenreAliasesForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "get_genre_id",
        "genre_name",
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "id",
        "name",
    )
    list_filter = (GenreIdFilter,)

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related("genre")
            .only("genre__id","genre__name","id","name","created_at","updated_at")
        )

    def get_genre_id(self, obj):
        return obj.genre.id

    get_genre_id.allow_tags = True  # type: ignore
    get_genre_id.short_description = "Genre id"  # type: ignore

    def genre_name(self, obj):
        return obj.genre.name

    genre_name.allow_tags = True  # type: ignore
    genre_name.short_description = "Genre"  # type: ignore


admin.site.register(Genres, GenresAdmin)
admin.site.register(GenreAliases, GenreAliasesAdmin)
