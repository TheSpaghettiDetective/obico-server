import logging
import dj_database_url
import re
import os
import sentry_sdk
import json
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

VERSION = os.environ.get('VERSION') or ''
SYNDICATE = os.environ.get('SYNDICATE') or 'base'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or 'cg#p$g+j9tax!#a3cup@1$8obt2_+&k3q+pmu)5%asj6yjpkag'

SESSION_COOKIE_AGE = 60 * 60 * 24 * 60  # User login session is 2 months
SESSION_COOKIE_REFRESH_INTERVAL = 60 * 60 * 24  # Refresh session cookies once every 24 hours
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_NAME = 'tsd_sessionid'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool('DEBUG', False)

ALLOWED_HOSTS = ['*']

## So that django will honor this header. Why is this not the default!
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'daphne',  # Need to declare this explicitly as of 4.0
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
    'whitenoise.runserver_nostatic',
    'hijack',
    'simple_history',
    'widget_tweaks',
    'rest_framework',
    'pushbullet',
    'corsheaders',
    'safedelete',
    'qr_code',
    'app',  # app has to come before allauth for template override to work
    "channels_presence",
    'oauth2_provider',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'api',
    'notifications',
    'webpack_loader',
]

if get_bool('SOCIAL_LOGIN', False):
    INSTALLED_APPS += [
        'allauth.socialaccount.providers.apple',
        'site_specific_allauth_google_provider',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'app.middleware.fix_tunnelv2_apple_cache',
    'app.middleware.TSDWhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'app.middleware.RefreshSessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'app.jusprin.middleware.jusprin_lang_middleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.middleware.TopDomainMatchingCurrentSiteMiddleware',
    'app.middleware.octoprint_tunnelv2',
    'app.middleware.check_admin_ip_whitelist',
    'allauth.account.middleware.AccountMiddleware',
    'hijack.middleware.HijackUserMiddleware',
    'app.middleware.check_x_api',
    'app.middleware.syndicate_header',
]

if DEBUG:
    # Add debug toolbar
    gzip_index = MIDDLEWARE.index('django.middleware.gzip.GZipMiddleware')
    MIDDLEWARE.insert(gzip_index+1, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INSTALLED_APPS.append("debug_toolbar")
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

    # Add nplusone
    INSTALLED_APPS.append('nplusone.ext.django')
    MIDDLEWARE.insert(gzip_index+1, 'nplusone.ext.django.NPlusOneMiddleware')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'notifications/plugins/email/templates/'),
            os.path.join(BASE_DIR, 'app/jusprin/templates/'),
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
                'app.context_processors.additional_context_export',
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

LANGUAGES = [
    ('en', 'English'),
    ('zh-cn', 'Simplified Chinese'),
    ('zh-tw', 'Traditional Chinese'),
    ('pt-br', 'Brazilian Portuguese'),
    ('es', 'Spanish'),
    ('de', 'German'),
    ('fr', 'French'),
    ('it', 'Italian'),
    ('ru', 'Russian'),
]


# Request logging for debugging purpose

NPLUSONE_LOG_LEVEL = logging.WARN

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'console_debug': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(name)-12s %(levelname)-8s %(message)s',
            'log_colors': {
                'DEBUG':    'bold_black',
                'INFO':     'white',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            },
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console_debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'console_debug'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
    },
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
}

if DEBUG and not get_bool('DISABLE_DEBUG_QUERY_LOGGING', False):
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console_debug'],
    }

# Django settings

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

X_FRAME_OPTIONS = 'SAMEORIGIN'

# This allows us to interact with the popup window during autodiscovery handshake
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'unsafe-none'

SITE_USES_HTTPS = get_bool('SITE_USES_HTTPS', False)
SITE_IS_PUBLIC = get_bool('SITE_IS_PUBLIC', False)

# DRF settings:

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '3600/hour',
        'user': '3600/hour',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('rest_framework.renderers.BrowsableAPIRenderer'),

# Google recaptcha V3

RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')

# Allauth

AUTHENTICATION_BACKENDS = (
    'app.accounts.SyndicateSpecificBackend',
    'oauth2_provider.backends.OAuth2Backend',
)
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username'
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if SITE_USES_HTTPS else 'http'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_ALLOW_SIGN_UP = get_bool('ACCOUNT_ALLOW_SIGN_UP', False)
ACCOUNT_ADAPTER = 'app.accounts.SyndicateSpecificAccountAdapter'
AUTH_USER_MODEL = 'app.User'
SOCIALACCOUNT_ADAPTER = 'app.accounts.SocialAccountAdapter'
SOCIALACCOUNT_PROVIDERS = {}
# Backwards compatibility to allow SSO via GET request
# We can remove this after we update to the mobile app to use POST instead of GET
SOCIALACCOUNT_LOGIN_ON_GET = True

if RECAPTCHA_SITE_KEY:
    ACCOUNT_FORMS = {'signup': 'app.forms.RecaptchaSignupForm'}

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24 * 365 * 100,  # 100 years
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'},
    'PKCE_REQUIRED': False,
    'ALLOWED_REDIRECT_URI_SCHEMES': ['http', 'https'],  # http to allow self-hosted servers
}

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
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://redis:6379'

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_build')
if not WEBPACK_LOADER_ENABLED:
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
WHITENOISE_AUTOREFRESH = get_bool('WHITENOISE_AUTOREFRESH', False)

TWILIO_COUNTRY_CODES = []  # serviced country codes, no restrictions by default

OCTOPRINT_TUNNEL_CAP = int(os.environ.get('OCTOPRINT_TUNNEL_CAP') or '1099511627776')  # 1TB by default
OCTOPRINT_TUNNEL_SUBDOMAIN_RE = re.compile(r'^(\w+)\.tunnels.*$')
OCTOPRINT_TUNNEL_PORT_RANGE = range(
        int(os.environ.get('OCTOPRINT_TUNNEL_PORT_RANGE').split('-')[0].strip('"\'')),
        int(os.environ.get('OCTOPRINT_TUNNEL_PORT_RANGE').split('-')[1].strip('"\'')),
    ) if os.environ.get('OCTOPRINT_TUNNEL_PORT_RANGE') else None

# settings exported to django templates
SETTINGS_EXPORT = [
    'VERSION',
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

LT_FILE_STORAGE_MODULE = os.environ.get('LT_FILE_STORAGE_MODULE') or 'lib.fs_file_storage'
ST_FILE_STORAGE_MODULE = os.environ.get('ST_FILE_STORAGE_MODULE') or 'lib.fs_file_storage'
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get(
    'GOOGLE_APPLICATION_CREDENTIALS')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(STATIC_ROOT, 'media')
INTERNAL_MEDIA_HOST = os.environ.get('INTERNAL_MEDIA_HOST')

PICS_CONTAINER = os.environ.get('PICS_CONTAINER', 'tsd-pics')
TIMELAPSE_CONTAINER = os.environ.get('TIMELAPSE_CONTAINER', 'tsd-timelapses')
GCODE_CONTAINER = os.environ.get('GCODE_CONTAINER', 'tsd-gcodes')
PUBLIC_VERSION_CONTAINER = os.environ.get('PUBLIC_VERSION_CONTAINER', 'public-versioned')

BUCKET_PREFIX = os.environ.get('BUCKET_PREFIX')
ML_API_HOST = os.environ.get('ML_API_HOST')
ML_API_TOKEN = os.environ.get('ML_API_TOKEN')

PIC_POST_LIMIT_PER_MINUTE = int(os.environ.get('PIC_POST_LIMIT_PER_MINUTE') or '0') # 0 means no limits
MIN_DETECTION_INTERVAL = 10 # 10s as the default interval between detections. Recommended not to change as the hyper parameters are tuned based on interval = 10s.

# Hyper parameters for prediction model
# Definitely not failing if ewm mean is below this level. =(0.4 - 0.02): 0.4 - optimal THRESHOLD_LOW in hyper params grid search; 0.02 - average of rolling_mean_short
THRESHOLD_LOW = float(os.environ.get('THRESHOLD_LOW') or '0.38')
# Definitely failing if ewm mean is above this level. =(0.8 - 0.02): 0.8 - optimal THRESHOLD_HIGH in hyper params grid search; 0.02 - average of rolling_mean_short
THRESHOLD_HIGH = float(os.environ.get('THRESHOLD_HIGH') or '0.78')
# The number of frames at the beginning of the print that are considered "safe"
INIT_SAFE_FRAME_NUM = int(os.environ.get('INIT_SAFE_FRAME_NUM') or '30')
# Print is failing is ewm mean is this many times over the short rolling mean
ROLLING_MEAN_SHORT_MULTIPLE = float(
    os.environ.get('ROLLING_MEAN_SHORT_MULTIPLE') or '3.8')
# The multiplication factor to escalate "warning" to "error"
ESCALATING_FACTOR = float(os.environ.get('ESCALATING_FACTOR') or '1.75')

# Event processing
PRINT_EVENT_HANDLER = 'app.tasks.process_print_events'

WELL_KNOWN_PATH = None

NOTIFICATION_PLUGIN_DIRS = [
    os.path.join(BASE_DIR, 'notifications/plugins'),
]

ADMIN_IP_WHITELIST = json.loads(os.environ.get('ADMIN_IP_WHITELIST') or '[]')

CSRF_TRUSTED_ORIGINS = json.loads(os.environ.get('CSRF_TRUSTED_ORIGINS') or '[]')

# JusPrin specific settings


# This line prevents warning messages after 3.2
# https://docs.djangoproject.com/en/4.0/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SYNDICATES = {
  'base': {
    'display_name': 'Obico',
    'from_email': DEFAULT_FROM_EMAIL,
    'docRoot': 'https://www.obico.io/docs/',
  },
  'jusprin': {
    'display_name': 'JusPrin',
    'from_email': 'JusPrin Support <support@obico.io>',
    'docRoot': 'https://www.obico.io/docs/',
    'logo_full': '/static/jusprin/img/jusprin-svg-logo-full.png',
  },
}
