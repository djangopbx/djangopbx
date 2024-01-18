#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2022 Adrian Fretwell <adrian@djangopbx.com>
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#
#    Contributor(s):
#    Adrian Fretwell <adrian@djangopbx.com>
#

"""
Django settings for pbx project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

# for bootstrap4 alert integration with django messages
from django.contrib.messages import constants as messages

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-aaabbbcccdddeeefff9876543210'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'bootstrap',
    'fontawesome',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'django_tables2',
    'django_ace',
    'portal.apps.PortalConfig',
    'tenants.apps.TenantsConfig',
    'switch.apps.SwitchConfig',
    'dialplans.apps.DialplansConfig',
    'musiconhold.apps.MusiconholdConfig',
    'recordings.apps.RecordingsConfig',
    'accounts.apps.AccountsConfig',
    'xmlhandler.apps.XmlhandlerConfig',
    'httapihandler.apps.HttapihandlerConfig',
    'voicemail.apps.VoicemailConfig',
    'xmlcdr.apps.XmlcdrConfig',
    'dashboard.apps.DashboardConfig',
    'firewall.apps.FirewallConfig',
    'status.apps.StatusConfig',
    'conferencesettings.apps.ConferencesettingsConfig',
    'provision.apps.ProvisionConfig',
    'contacts.apps.ContactsConfig',
    'ringgroups.apps.RinggroupsConfig',
    'phrases.apps.PhrasesConfig',
    'utilities.apps.UtilitiesConfig',
    'numbertranslations.apps.NumbertranslationsConfig',
    'ivrmenus.apps.IvrmenusConfig',
    'callflows.apps.CallflowsConfig',
    'callblock.apps.CallblockConfig',
    'callcentres.apps.CallcentresConfig',
    'autoreports.apps.AutoreportsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Uncomment below to allow language selection based on data from the request. It customises content for each user.
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 300,
        'KEY_PREFIX': 'pbx',
        "OPTIONS": {
            "no_delay": True,
            "ignore_exc": True,
            "max_pool_size": 8,
            "use_pooling": True,
        },
    }
}

LOGGING = {
    'version': 1,                       # the dictConfig format version
    'disable_existing_loggers': False,  # retain the default loggers
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'general.log',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['file'],
        },
    },
    'formatters': {
        'verbose': {
            'format': '{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
}

ROOT_URLCONF = 'pbx.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pbx.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'djangopbx',
        'USER': 'djangopbx',
        'PASSWORD': 'postgres-insecure-abcdef9876543210',
        'HOST': '127.0.0.1',
        'PORT': '5432'
# removed CONN_MAX_AGE as it was causing a Server 500 error after a uwsgi restart/reload
# exceptions were:
#      psycopg2.OperationalError: SSL SYSCALL error: EOF detected
#      AttributeError: 'SessionStore' object has no attribute '_session_cache'
#        'CONN_MAX_AGE': 300
    },
    'freeswitch': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'freeswitch',
        'USER': 'freeswitch',
        'PASSWORD': 'postgres-insecure-abcdef9876543210',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = '/var/www/static/'

# For model.FileField storage
MEDIA_ROOT = '/home/django-pbx/media'

# This setting defines the additional locations the staticfiles app will traverse
# if the FileSystemFinder finder is enabled
# e.g. if you use the collectstatic or findstatic management command or use the static file serving view.

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/portal/auth/login/'
LOGIN_REDIRECT_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        #'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.DjangoModelPermissions',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Uncomment for production
# SESSION_COOKIE_AGE = 3600
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Settings for django-import-export
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_IMPORT_PERMISSION_CODE = 'Add'

# Settings for django-tables2
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap-responsive.html"
DJANGO_TABLES2_PAGE_RANGE = 8


MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

# event socket connection info
EVSKT = ('127.0.0.1', 8021, 'ClueCon')

# show all tables in Admin - useful for imports and exports
PBX_ADMIN_SHOW_ALL = False

# New in Django 4.1.   If set to True, existing persistent database connections will be
# health checked before they are reused in each request performing database access.
CONN_HEALTH_CHECKS = True
