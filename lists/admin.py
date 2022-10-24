import re

from django import forms
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.db.models import Count
from .models import Lists, ListsMovies


class ListFilter(admin.SimpleListFilter):
    title = "Layout"
    parameter_name = "layout"

    def lookups(self, request, model_admin):
        return (
            ("default", "default"),
            ("top-left", "top-left"),
            ("bottom-left", "bottom-left"),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset.filter(layout="default")
        else:
            return queryset.filter(layout=self.value())


class ListsForm(forms.ModelForm):
    active = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        layout = None
        super().__init__(*args, **kwargs)
        self.fields["layout"].choices = (
            ("default", "default"),
            ("top-left", "top-left"),
            ("bottom-left", "bottom-left"),
            ("", ""),
        )
        self.fields["active"].label = mark_safe("<strong>Active</strong>")
        self.fields["active"].initial = self.fields["active"]
        self.fields["active"].choices = ((0, "0"), (1, "1"))

        if kwargs.get("instance"):
            instance = kwargs["instance"]
            layout = instance.layout

        self.fields["layout"].initial = layout if layout else ""

    class Meta:
        model = Lists
        fields = "__all__"
        exclude = ["created_at", "updated_at"]


class ListsAdmin(admin.ModelAdmin):
    form = ListsForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "name",
        "de_name",
        "layout",
        "active",
        "popularity",
        "infos_view",
    )
    search_fields = ("id", "name", "de_name")
    list_filter = (ListFilter,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(Count('list_movies', distinct=True))

    def infos_view(self, obj):
        return format_html(
            '<a href="/admin/lists/listsmovies/?list_id=%s">%s</a>'
            % (obj.id, obj.list_movies__count)
        )

    infos_view.allow_tags = True  # type: ignore
    infos_view.short_description = "Infos"  # type: ignore


# ____________________ LISTS MOVIES ____________________


class ListsMoviesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        list_id = None
        super().__init__(*args, **kwargs)

        if kwargs.get("initial"):
            path = kwargs["initial"].get("_changelist_filters")
            if "list_id" in path:
                list_id = re.findall("list_id=\d+", path)
                if list_id:
                    list_id = list_id[0]
                    list_id = re.findall("\d+", list_id)[0]
                elif "%3D" in path:
                    list_id = path.split("%3D")[-1]

        self.fields["list"].initial = list_id

    class Meta:
        model = ListsMovies
        fields = "__all__"
        exclude = ["created_at", "updated_at"]


class ListIdFilter(admin.SimpleListFilter):
    title = "List Id"
    parameter_name = "list_id"

    def lookups(self, request, model_admin):
        lists = set([c for c in Lists.objects.all()])
        return [(c.id, f"{c.id} ({c.name})") for c in lists]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(list_id=self.value())
        else:
            return queryset


class ListsMoviesAdmin(admin.ModelAdmin):
    raw_id_fields = ["movie", "list"]
    form = ListsMoviesForm
    change_form_template = "admin/button_change_form.html"
    list_display = (
        "id",
        "list",
        "movie_name",
    )
    search_fields = (
        "id",
        "movie_name",
    )
    list_filter = (ListIdFilter,)

    def movie_name(self, obj):
        return obj.movie.original_title

    movie_name.allow_tags = True  # type: ignore
    movie_name.short_description = "movie name"  # type: ignore


admin.site.register(Lists, ListsAdmin)
admin.site.register(ListsMovies, ListsMoviesAdmin)
