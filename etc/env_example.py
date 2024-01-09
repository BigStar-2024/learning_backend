import os
import json
import configparser

from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'este es el super secreto '

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']




CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://localhost:8000',
)


SITE_ID = 1

ENV_INSTALLED_APPS = []



DEFAULT_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DATABASES = (
    json.loads(os.environ["APP_DATABASES"]) if "APP_DATABASES" in os.environ else DEFAULT_DATABASES
)

# Parse config fils to work with postgres
# Only in postgres one cfg file can have multiple databases config
#     separated by sections ex [default]
for db_name, db_config in DATABASES.items():
    if DATABASES[db_name]['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        if 'read_default_file' in DATABASES[db_name]['OPTIONS']:
            cfg_file = DATABASES[db_name]['OPTIONS']['read_default_file']
            config = configparser.ConfigParser()
            config.read(cfg_file)
            for key in config[db_name]:
                DATABASES[db_name][key.upper()] = config[db_name][key]
            del(DATABASES[db_name]['OPTIONS'])



PARLER_LANGUAGES = {
    1: (
        {'code': 'en-us',},
        {'code': 'es-mx',},
    ),
    'default': {
        'fallback': 'en-us',             # defaults to PARLER_DEFAULT_LANGUAGE_CODE
        'hide_untranslated': False,   # the default; let .active_translations() return fallbacks too.
    }
}


SENDGRID_API_KEY = 'llave de sendrgrid'
SENDGRID_DEFAULT_SENDER = 'Learn With Socrates <noreply@practiceplaygrow.com>'




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'website/static'),
]


STATIC_URL =  '/static/'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey' # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
DEFAULT_FROM_EMAIL = SENDGRID_DEFAULT_SENDER

