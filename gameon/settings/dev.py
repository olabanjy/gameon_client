from .base import *

from celery.schedules import crontab

DEBUG = True

# ALLOWED_HOSTS = ["*"]
# ALLOWED_HOSTS = ["gameon.com.ng", "3.87.216.135"]
ALLOWED_HOSTS = ["gameon-ng.herokuapp.com"]


INSTALLED_APPS += [
    "debug_toolbar",
    "django_user_agents",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "ipinfo_django.middleware.IPinfo",
]


DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db2.sqlite3",
    }
}


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.zoho.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# DEFAULT_FROM_EMAIL = config("EMAIL_HOST_USER")
# EMAIL_HOST_USER = config("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
# ADMINS = (("Support", f"{config('ADMINS_USER')}"),)

EMAIL_HOST = "smtp.zoho.com"
EMAIL_HOST_USER = "noreply@gameon.com.ng"
EMAIL_HOST_PASSWORD = "Pq3SwK52Jti5"
ADMINS_USER = "noreply@gameon.com.ng"

DEFAULT_FROM_EMAIL = "Game On <noreply@gameon.com.ng>"


# CELERY related settings
BROKER_URL = "amqp://localhost"
# CELERY_RESULT_BACKEND = 'amqp://'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Lagos"


# AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")


AWS_ACCESS_KEY_ID = "AKIAQFIADKCN7WE2D5QD"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "game-on-files"


AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
# AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")
# DEFAULT_FILE_STORAGE = config("DEFAULT_FILE_STORAGE")
AWS_S3_REGION_NAME = "us-east-1"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"


# IPINFO_TOKEN = config("IPINFO_TOKEN")
IPINFO_TOKEN = "9f438262432756"


# IPINFO_SETTINGS = {
#     'cache_options': {
#         'ttl': 30,
#         'maxsize': 128
#     }
# }


CELERY_BEAT_SCHEDULE = {}


# TEST_PAYSTACK_SECRET_KEY = config("TEST_PAYSTACK_SECRET_KEY")
# TEST_PAYSTACK_PUBLIC_KEY = config("TEST_PAYSTACK_PUBLIC_KEY")
# LIVE_PAYSTACK_SECRET_KEY = config("LIVE_PAYSTACK_SECRET_KEY")
# LIVE_PAYSTACK_PUBLIC_KEY = config("LIVE_PAYSTACK_PUBLIC_KEY")


TEST_PAYSTACK_SECRET_KEY = "sk_test_3d4ea6e92be4651de9b3c562579523ef1fcf3970"
TEST_PAYSTACK_PUBLIC_KEY = "pk_test_ea794f8358c6ebfe9f98e0c4fba980b2797343e5"


LIVE_PAYSTACK_SECRET_KEY = "sk_live_43121ac0dc5798c513eed66d052abe2421672c6e"
LIVE_PAYSTACK_PUBLIC_KEY = "pk_live_cb63032fbb2469af6fa0cc75e6ea0dfc727ebe29"


PAYPAL_RECEIVER_EMAIL = "syiflawless@gmail.com"

PAYPAL_TEST = True

GAMEON_ADMIN_LAT = 6.4414728785821636
GAMEON_ADMIN_LONG = 3.4585855392759584
