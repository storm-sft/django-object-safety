# Starts a test server

import os

import django
from django.conf import settings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "safety"))


def boot_django():
    settings.configure(
        BASE_DIR=BASE_DIR,
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
            }
        },

        AUTH_USER_MODEL="safety_tests.RemoteUser",
        SAFETY_USER_REMOTE_URL="https://jsonplaceholder.typicode.com/users",

        INSTALLED_APPS=[
            "safety_tests",
            "safety",
            "django_fake_model",
            "django.contrib.auth",
            "django.contrib.contenttypes",
        ],

        SAFETY_PERMISSION_GROUP_MODEL="safety.PermissionGroup",
        TIME_ZONE="UTC",
        USE_TZ=True,
        USE_I18N=True,
    )

    django.setup()
