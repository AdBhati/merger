"""Production settings and globals."""
from .common import *  # noqa
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import os
from urllib.parse import urlparse

# Database
DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "zuperscore",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
    }
}

# Parse database configuration from $DATABASE_URL
DATABASES["default"] = dj_database_url.config()
SITE_ID = 1

sentry_sdk.init(
    dsn="https://765631745bc14a08be3699545c4b5dc8@o1063442.ingest.sentry.io/6525329",
    integrations=[DjangoIntegration(), RedisIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    environment="staging",
    traces_sample_rate=0.7,
)

# Enable Connection Pooling (if desired)
# DATABASES['default']['ENGINE'] = 'django_postgrespool'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow all host headers
ALLOWED_HOSTS = ["*"]

# CORS allow all on staging
CORS_ORIGIN_ALLOW_ALL = True


INSTALLED_APPS.append("django_s3_storage")


# Enable Connection Pooling (if desired)
# DATABASES['default']['ENGINE'] = 'django_postgrespool'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow all host headers
ALLOWED_HOSTS = [
    "*",
]

DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
# Simplified static file serving.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


REDIS_URL = urlparse(os.environ.get("REDIS_URL"))

# Caching

REDIS_SUB_URL = os.environ.get("REDIS_SUB_URL")

WEB_URL = "https://zuperscore-staging.vercel.app"

# celery settings
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0") + "?ssl_cert_reqs=CERT_NONE"
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0") + "?ssl_cert_reqs=CERT_NONE"
