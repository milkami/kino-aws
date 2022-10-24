from django.urls import path, reverse

from .views import ignore_movie, run_parser

urlpatterns = [
    path("cinemas/ignore_movie/<id>", ignore_movie),
    path("cinemas/run_parser", run_parser),
]
