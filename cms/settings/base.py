"""
Django settings for cms project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path

import django_heroku
import pymysql
pymysql.version_info = (1, 4, 2, "final", 0)
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []  # type: ignore

# INTERNAL_IPS = [
#     # ...
#     "127.0.0.1",
#     # ...
# ]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "movies.apps.MoviesConfig",
    "tvshows.apps.TvshowsConfig",
    "cinemas.apps.CinemasConfig",
    "services.apps.ServicesConfig",
    "charts.apps.ChartsConfig",
    "lists.apps.ListsConfig",
    "genres.apps.GenresConfig",
    "distributors.apps.DistributorsConfig",
    "media.apps.MediaConfig",
    "spotlights.apps.SpotlightsConfig",
    "other.apps.OtherConfig",
    "stats.apps.StatsConfig",
    "storages",
    "people.apps.PeopleConfig",
    "background_task",
    # "debug_toolbar",
]

STATIC_URL = "static/"

MIDDLEWARE = [
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cms.urls"

import os

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DIRNAME = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIRS = (os.path.join(BASE_DIR, "/templates/"),)

WSGI_APPLICATION = "cms.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# current used db is staging (host for prod. has to be set in config first)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PW"),
        "HOST": os.getenv("DB_HOST_PRODUCTION"),
        "PORT": "3306",
        "OPTIONS": {
            "ssl": {
                "ca": os.path.join(
                    os.path.dirname(os.path.abspath("rds-ca-2019-root.pem")),
                    "certificates",
                    "rds-ca-2019-root.pem",
                )
            },
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ordering list

ADMIN_ORDERING = [
    (
        "movies",
        [
            "Movies",
            "Infos",
            "InfosWithShowtimes",
            "InfosWithHotShowtimes",
            "AtInfosWithShowtimes",
            "ChInfosWithShowtimes",
        ],
    ),
    (
        "cinemas",
        [
            "Chains",
            "Cinemas",
            "Parsers",
            "Showtimes",
            "NewKinoheldCinemas",
            "RemovedKinoheldCinemas",
        ],
    ),
    ("tvshows", ["TvShows", "TvShowTranslations", "Seasons", "Episodes"]),
    (
        "services",
        [
            "Services",
            "MoviesServices",
            "SeasonServices",
        ],
    ),
    (
        "media",
        [
            "Media",
        ],
    ),
    (
        "spotlights",
        [
            "Spotlights",
        ],
    ),
    (
        "charts",
        [
            "Charts",
        ],
    ),
    ("lists", ["Lists", "ListsMovies"]),
    (
        "distributors",
        [
            "Distributors",
        ],
    ),
    (
        "people",
        [
            "People",
        ],
    ),
    ("genres", ["GenreAliases", "Genres"]),
    ("auth", ["User", "Group"]),
    ("other", ["Admins"]),
    ("stats", ["Statistics"]),
]


# sort function
def get_app_list(self, request):
    app_dict = self._build_app_dict(request)
    app_dict["cinemas"]["models"] = [
        i for i in app_dict["cinemas"]["models"] if i["object_name"] != "MoviePlaylist"
    ]
    for app_name, object_list in ADMIN_ORDERING:
        app = app_dict[app_name]
        app["models"].sort(key=lambda x: object_list.index(x["object_name"]))
        yield app


from django.contrib import admin

admin.AdminSite.get_app_list = get_app_list

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

DATE_FORMAT = "d.m.Y"
TIME_FORMAT = "H:i"
DATETIME_FORMAT = "d.m.Y, H:i"
USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

AWS_DEFAULT_ACL = None

django_heroku.settings(locals())
