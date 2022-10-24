import os

import dj_database_url

from cms.settings.base import *

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
                ),
                "sslmode": "VERIFY_IDENTITY",
            },
        },
    }
}
