"""Development settings and globals."""

from __future__ import absolute_import
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration


from .common import *  # noqa


DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "zuperscore_prod_db",
        "USER": "postgres",
        "PASSWORD": "m8XzbVnMfZSJfOHI6z2A",
        "HOST": "zuperscore-production.ctdcxbtpmgmd.ap-south-1.rds.amazonaws.com",
    }


    # "default": {
    #     "ENGINE": "django.db.backends.postgresql_psycopg2",
    #     "NAME": "d5rhp1f2jpqd71",
    #     "USER": "u3k2pafkhimndq",
    #     "PASSWORD": "pd19dfecbe12e0cbd2ddd68cab4b5d453fc35190cc568541ec245838cf937c427",
    #     "HOST": "ec2-44-213-9-110.compute-1.amazonaws.com",
    # },
}





CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

INSTALLED_APPS += ("debug_toolbar",)

MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = ("127.0.0.1",)

CORS_ORIGIN_ALLOW_ALL = True

sentry_sdk.init(
    dsn="https://765631745bc14a08be3699545c4b5dc8@o1063442.ingest.sentry.io/6525329",
    integrations=[DjangoIntegration(), RedisIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    environment="local",
    traces_sample_rate=0.7,
)

WEB_URL = "http://localhost:8000"

RQ_QUEUES = {
    "default": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": 360,
    },
    "section_submission": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": 360,
    },
    "section_block_submission": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": 360,
    },
}
