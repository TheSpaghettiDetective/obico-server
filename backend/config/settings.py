import logging
import dj_database_url
import re
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from django.contrib.messages import constants as messages


def get_bool(key, default):
    if key in os.environ:
        return os.environ[key].strip('\'"').lower() == 'true'
    return default


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VERSION = os.environ.get('VERSION', '')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', 'cg#p$g+j9tax!#a3cup@1$8obt2_+&k3q+pmu)5%asj6yjpkag')

SESSION_COOKIE_AGE = 60 * 60 * 24 * 60  # User login session is 2 months
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_NAME = 'tsd_sessionid'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool('DEBUG', False)

ALLOWED_HOSTS = ['*']

## So that django will honor this header. Why is this not the default!
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'django.contrib.humanize',
    'channels',
    "channels_presence",
    'whitenoise.runserver_nostatic',
    'hijack',
    'compat',
    'simple_history',
    'widget_tweaks',
    'rest_framework',
    'bootstrap_pagination',
    'jstemplate',
    'pushbullet',
    'corsheaders',
    'safedelete',
    'nplusone.ext.django',
    'qr_code',
    'app',  # app has to come before allauth for template override to work
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'api',
    'notifications',
    'webpack_loader',
]

if get_bool('SOCIAL_LOGIN', False):
    INSTALLED_APPS += [
        'allauth.socialaccount.providers.facebook',
        'allauth.socialaccount.providers.google',
        'allauth.socialaccount.providers.apple',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'app.middleware.fix_tunnelv2_apple_cache',
    'app.middleware.TSDWhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'nplusone.ext.django.NPlusOneMiddleware',
    'app.middleware.rename_session_cookie',
    'app.middleware.SessionHostDomainMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.middleware.octoprint_tunnelv2',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'notifications/plugins/email/templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
                'app.context_processors.additional_settings_export',
                'app.context_processors.detect_app_platform',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.routing.application'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Request logging for debugging purpose

NPLUSONE_LOG_LEVEL = logging.WARN

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
}

# Django settings

DATA_UPLOAD_MAX_MEMORY_SIZE = 200 * 1024 * 1024

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_build')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../frontend/static'),
    os.path.join(BASE_DIR, '../frontend/builds'),
]
# WHITENOISE_KEEP_ONLY_HASHED_FILES = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'zip',
    'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br', 'swf',
    'flv', 'woff', 'woff2', 'map'  # added map
)

SITE_ID = 1
SITE_USES_HTTPS = get_bool('SITE_USES_HTTPS', False)
SITE_IS_PUBLIC = get_bool('SITE_IS_PUBLIC', False)

# DRF settings:

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '3600/hour',
    },
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# Google recaptcha V3

RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

# Allauth

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if SITE_USES_HTTPS else 'http'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_ALLOW_SIGN_UP = get_bool('ACCOUNT_ALLOW_SIGN_UP', False)

AUTH_USER_MODEL = 'app.User'
SOCIALACCOUNT_ADAPTER = 'app.accounts.SocialAccountAdapter'
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'VERIFIED_EMAIL': True
    }
}

if RECAPTCHA_SITE_KEY:
    ACCOUNT_FORMS = {'signup': 'app.forms.RecaptchaSignupForm'}

# Layout
TEMPLATE_LAYOUT = "layout.html"

# Sentry

SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            LoggingIntegration(
                level=logging.INFO, # Capture info and above as breadcrumbs
                event_level=None  # Send logs as events above a logging level, disabled it
            ),
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,

        # By default the SDK will try to use the SENTRY_RELEASE
        # environment variable, or infer a git commit
        # SHA as release, however you may want to set
        # something more human-readable.
        # release="myapp@1.0.0",
        release=VERSION,
    )

# REDIS client
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379')

# Django cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Django Email settings

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TLS = get_bool('EMAIL_USE_TLS', False)

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# webpack bundle stats

WEBPACK_LOADER_ENABLED = get_bool('WEBPACK_LOADER_ENABLED', False)
WEBPACK_STATS_PATH = os.path.join(
    BASE_DIR, '../frontend/webpack-stats.json')
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'frontend/',  # must end with slash
        'STATS_FILE': WEBPACK_STATS_PATH,
        'POLL_INTERVAL': 0.5,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
    }
}


TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')
TWILIO_COUNTRY_CODES = []  # serviced country codes, no restrictions by default
TWILIO_ENABLED = TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER

PUSHOVER_APP_TOKEN = os.environ.get('PUSHOVER_APP_TOKEN')

OCTOPRINT_TUNNEL_CAP = int(os.environ.get('OCTOPRINT_TUNNEL_CAP', '1099511627776'))  # 1TB by default
OCTOPRINT_TUNNEL_SUBDOMAIN_RE = re.compile(r'^(\w+)\.tunnels.*$')
OCTOPRINT_TUNNEL_PORT_RANGE = range(
        int(os.environ.get('OCTOPRINT_TUNNEL_PORT_RANGE').split('-')[0].strip('"\'')),
        int(os.environ.get('OCTOPRINT_TUNNEL_PORT_RANGE').split('-')[1].strip('"\'')),
    ) if os.environ.get('OCTOPRINT_TUNNEL_PORT_RANGE') else None

# settings export
SETTINGS_EXPORT = [
    'VERSION',
    'TWILIO_ENABLED',
    'PUSHOVER_APP_TOKEN',
    'TEMPLATE_LAYOUT',
    'ACCOUNT_ALLOW_SIGN_UP',
    'RECAPTCHA_SITE_KEY',
    'SENTRY_DSN',
]

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Channels layers
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
            'capacity': 1500,
            'expiry': 60,
        },
    },
}

# Settings to store and serve uploaded images
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get(
    'GOOGLE_APPLICATION_CREDENTIALS')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media')
INTERNAL_MEDIA_HOST = os.environ.get('INTERNAL_MEDIA_HOST')
PICS_CONTAINER = 'tsd-pics'
TIMELAPSE_CONTAINER = 'tsd-timelapses'
GCODE_CONTAINER = 'tsd-gcodes'

BUCKET_PREFIX = os.environ.get('BUCKET_PREFIX')
ML_API_HOST = os.environ.get('ML_API_HOST')
ML_API_TOKEN = os.environ.get('ML_API_TOKEN')

# Hyper parameters for prediction model
# Definitely not failing if ewm mean is below this level. =(0.4 - 0.02): 0.4 - optimal THRESHOLD_LOW in hyper params grid search; 0.02 - average of rolling_mean_short
THRESHOLD_LOW = float(os.environ.get('THRESHOLD_LOW', '0.38'))
# Definitely failing if ewm mean is above this level. =(0.8 - 0.02): 0.8 - optimal THRESHOLD_HIGH in hyper params grid search; 0.02 - average of rolling_mean_short
THRESHOLD_HIGH = float(os.environ.get('THRESHOLD_HIGH', '0.78'))
# The number of frames at the beginning of the print that are considered "safe"
INIT_SAFE_FRAME_NUM = int(os.environ.get('INIT_SAFE_FRAME_NUM', 30))
# Print is failing is ewm mean is this many times over the short rolling mean
ROLLING_MEAN_SHORT_MULTIPLE = float(
    os.environ.get('ROLLING_MEAN_SHORT_MULTIPLE', 3.8))
# The multiplication factor to escalate "warning" to "error"
ESCALATING_FACTOR = float(os.environ.get('ESCALATING_FACTOR', 1.75))

# Event processing
PRINT_EVENT_HANDLER = 'app.tasks.process_print_events'

WELL_KNOWN_PATH = None

NOTIFICATION_PLUGIN_DIRS = [
    os.path.join(BASE_DIR, 'notifications/plugins'),
]
