import os
import datetime
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = "2rqqp7=s2wr09w8q+t)rl=5v&1$5yizqj%n6zn)^-03bt3i)-h"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Inhouse apps
    "zuperscore.analytics",
    "zuperscore.api",
    "zuperscore.bgtasks",
    "zuperscore.db",
    "zuperscore.utils",
    "zuperscore.web",
    "zuperscore.middleware",
    "zuperscore.email_templates",
    # Third-party things
    "django_rq",
    "rest_framework",
    "corsheaders",
    "taggit",
    "silk",
    # "background_task"
    "celery",
]

MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    # "DEFAULT_PAGINATION_CLASS": 'rest_framework.pagination.PageNumberPagination',
    # "PAGE_SIZE": 10
}

SPECTACULAR_SETTINGS = {"TITLE": "ZuperScore-Dev"}

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)  # default

ROOT_URLCONF = "zuperscore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
            os.path.join("zuperscore", "email_templates"),
        ],
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




WSGI_APPLICATION = "zuperscore.wsgi.application"

# Django Sites

SITE_ID = 1

# User Model
AUTH_USER_MODEL = "db.User"

# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation

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

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static-assets", "collected-static")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Media Settings
MEDIA_ROOT = "mediafiles"
MEDIA_URL = "/media/"


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# Host for sending e-mail.
EMAIL_HOST = "replace-me"
# Port for sending e-mail.
EMAIL_PORT = 587
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = "replace-me"
EMAIL_HOST_PASSWORD = "replace-me"
EMAIL_USE_TLS = True

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10080),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=43200),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("JWT",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# Site Settings

AUTH_USER_MODEL = "db.User"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# Host for sending e-mail.
EMAIL_HOST = "smtp.sendgrid.net"
# Port for sending e-mail.
EMAIL_PORT = 587
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY")
EMAIL_USE_TLS = True


# The AWS region to connect to.
AWS_REGION = "ap-south-1"

# The AWS access key to use.

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY')

# The AWS secret access key to use.

AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_KEY')

# The optional AWS session token to use.
AWS_SESSION_TOKEN = ""

# The name of the bucket to store files in.
# AWS_S3_BUCKET_NAME = "library-asset"
AWS_S3_BUCKET_NAME = 'library-asset'

# How to construct S3 URLs ("auto", "path", "virtual").
AWS_S3_ADDRESSING_STYLE = "auto"

# The full URL to the S3 endpoint. Leave blank to use the default region URL.
AWS_S3_ENDPOINT_URL = ""

# A prefix to be applied to every stored file. This will be joined to every filename using the "/" separator.
AWS_S3_KEY_PREFIX = ""

# Whether to enable authentication for stored files. If True, then generated URLs will include an authentication
# token valid for `AWS_S3_MAX_AGE_SECONDS`. If False, then generated URLs will not include an authentication token,
# and their permissions will be set to "public-read".
AWS_S3_BUCKET_AUTH = False

# How long generated URLs are valid for. This affects the expiry of authentication tokens if `AWS_S3_BUCKET_AUTH`
# is True. It also affects the "Cache-Control" header of the files.
# Important: Changing this setting will not affect existing files.
AWS_S3_MAX_AGE_SECONDS = 60 * 60  # 1 hours.

# A URL prefix to be used for generated URLs. This is useful if your bucket is served through a CDN. This setting
# cannot be used with `AWS_S3_BUCKET_AUTH`.
AWS_S3_PUBLIC_URL = ""

# If True, then files will be stored with reduced redundancy. Check the S3 documentation and make sure you
# understand the consequences before enabling.
# Important: Changing this setting will not affect existing files.
AWS_S3_REDUCED_REDUNDANCY = False

# The Content-Disposition header used when the file is downloaded. This can be a string, or a function taking a
# single `name` argument.
# Important: Changing this setting will not affect existing files.
AWS_S3_CONTENT_DISPOSITION = ""

# The Content-Language header used when the file is downloaded. This can be a string, or a function taking a
# single `name` argument.
# Important: Changing this setting will not affect existing files.
AWS_S3_CONTENT_LANGUAGE = ""

# A mapping of custom metadata for each file. Each value can be a string, or a function taking a
# single `name` argument.
# Important: Changing this setting will not affect existing files.
AWS_S3_METADATA = {}

# If True, then files will be stored using AES256 server-side encryption.
# If this is a string value (e.g., "aws:kms"), that encryption type will be used.
# Otherwise, server-side encryption is not be enabled.
# Important: Changing this setting will not affect existing files.
AWS_S3_ENCRYPT_KEY = False

# The AWS S3 KMS encryption key ID (the `SSEKMSKeyId` parameter) is set from this string if present.
# This is only relevant if AWS S3 KMS server-side encryption is enabled (above).
# AWS_S3_KMS_ENCRYPTION_KEY_ID = ""

# If True, then text files will be stored using gzip content encoding. Files will only be gzipped if their
# compressed size is smaller than their uncompressed size.
# Important: Changing this setting will not affect existing files.
AWS_S3_GZIP = True

# The signature version to use for S3 requests.
AWS_S3_SIGNATURE_VERSION = None

# If True, then files with the same name will overwrite each other. By default it's set to False to have
# extra characters appended.
AWS_S3_FILE_OVERWRITE = False

# AWS Settings End
