"""
Django settings for config project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local development variables from BASE_DIR/.env if it exists.
# Variables already set in the environment take precedence.
load_dotenv(BASE_DIR / '.env')


def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


# SECURITY WARNING: don't run with debug turned on in production!
# Off unless DJANGO_DEBUG=true (set it in your local .env).
DEBUG = os.environ.get('DJANGO_DEBUG', '').lower() in ('1', 'true', 'yes')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set DJANGO_SECRET_KEY (see .env.example).')
    SECRET_KEY = 'django-insecure-local-development-only'

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
# Full origins (https://shop.example.com) allowed to POST forms behind HTTPS.
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')
# Render sets this to the service's onrender.com host name, so no host
# variables are needed there unless you add a custom domain.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',
    'pages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'pages.context_processors.business',
                'catalog.context_processors.nav_services',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# PostgreSQL only: the local server in development, a hosted one (e.g.
# Supabase) later. Configure either DATABASE_URL (preferred) or the individual
# DB_* variables. There is deliberately no SQLite fallback.

SECURE_SSLMODES = {'require', 'verify-ca', 'verify-full'}
LOCAL_HOSTS = {'localhost', '127.0.0.1', '::1'}


def database_from_env():
    url = os.environ.get('DATABASE_URL')
    if url:
        parts = urlsplit(url)
        if parts.scheme not in ('postgres', 'postgresql'):
            raise ImproperlyConfigured('DATABASE_URL must be a postgresql:// URL.')
        query = parse_qs(parts.query)
        config = {
            'NAME': unquote(parts.path.lstrip('/')) or 'postgres',
            'USER': unquote(parts.username or ''),
            'PASSWORD': unquote(parts.password or ''),
            'HOST': parts.hostname or '',
            'PORT': str(parts.port or 5432),
        }
        url_sslmode = query.get('sslmode', [None])[0]
    else:
        missing = [
            name for name in ('DB_HOST', 'DB_USER', 'DB_PASSWORD')
            if not os.environ.get(name)
        ]
        if missing:
            raise ImproperlyConfigured(
                'Database is not configured. Set DATABASE_URL or '
                + ', '.join(missing) + ' (see .env.example).'
            )
        config = {
            'NAME': os.environ.get('DB_NAME', 'postgres'),
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASSWORD'],
            'HOST': os.environ['DB_HOST'],
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
        url_sslmode = None

    if not (config['HOST'] and config['USER'] and config['PASSWORD']):
        raise ImproperlyConfigured('DATABASE_URL must include user, password, and host.')

    # Hosted databases require encrypted connections; weaker modes (e.g.
    # sslmode=disable) are accepted only for a local PostgreSQL server.
    sslmode = os.environ.get('DB_SSLMODE') or url_sslmode or 'require'
    if sslmode not in SECURE_SSLMODES and config['HOST'] not in LOCAL_HOSTS:
        raise ImproperlyConfigured(
            f'DB_SSLMODE must be one of {sorted(SECURE_SSLMODES)}, got {sslmode!r}.'
        )
    options = {'sslmode': sslmode}
    if os.environ.get('DB_SSLROOTCERT'):
        options['sslrootcert'] = os.environ['DB_SSLROOTCERT']

    return {
        'ENGINE': 'django.db.backends.postgresql',
        **config,
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': options,
    }


DATABASES = {
    'default': database_from_env(),
}

TEST_RUNNER = 'config.test_runner.PoolerSafeTestRunner'


# Authentication and sessions (Django's built-in auth; no public registration yet)

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'pages:home'
LOGOUT_REDIRECT_URL = 'pages:home'

SESSION_COOKIE_AGE = 8 * 60 * 60  # one working day
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
# Send cookies over HTTPS only once DEBUG is off.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
# A host like Render terminates TLS at its proxy and forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', str(not DEBUG)).lower() in ('1', 'true', 'yes')
# The host's health checks may arrive over plain HTTP; answer them directly.
SECURE_REDIRECT_EXEMPT = [r'^healthz$']


# Business details shown on every page (pages.context_processors.business).
# The defaults are placeholders until the owner confirms the real ones.

BUSINESS_NAME = os.environ.get('BUSINESS_NAME', 'Brightwell Home Cleaning')
BUSINESS_PHONE = os.environ.get('BUSINESS_PHONE', '(555) 010-0199')
BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL', 'hello@example.com')
BUSINESS_SERVICE_AREA = os.environ.get('BUSINESS_SERVICE_AREA', 'Hartford County, Connecticut')
BUSINESS_HOURS = os.environ.get('BUSINESS_HOURS', 'Monday to Saturday, 8 am to 6 pm')


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Bookings will be scheduled in the business's local time.
TIME_ZONE = os.environ.get('DJANGO_TIME_ZONE', 'America/New_York')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# WhiteNoise serves collected static files in production. Compression without a
# manifest, so templates render in tests without running collectstatic first.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
