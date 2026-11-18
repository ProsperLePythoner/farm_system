"""
Project settings: environment-based configuration for local and hosted runs.

WHAT THIS FILE DOES
    Tells Django which apps, middleware, templates, database, authentication,
    timezone, and static-file paths to use.

WHERE IT FITS
    Django loads this module through DJANGO_SETTINGS_MODULE. config/urls.py
    provides the root routes and config/wsgi.py / config/asgi.py use it when
    starting the application.

KEY DECISIONS
    Credentials and deployment-specific values come from the environment so
    local and hosted environments can use separate settings without storing
    secrets in source control.
"""

from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load local development values when a .env file exists; deployment platforms
# normally provide the same settings directly as environment variables.
load_dotenv(BASE_DIR / ".env")


# Django requires a private key for signing sessions and other security data.
# If unset, this is None and Django's system check will report an invalid setup.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# Only the literal value "true" (case-insensitive) enables debug pages; missing
# or any other value keeps DEBUG off, which avoids exposing tracebacks by default.
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"

# Hosts are comma-separated. An empty value leaves no allowed production hosts,
# so requests with ordinary host headers will be rejected by Django.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# Vercel provides its deployment hostname separately; add it to Django's
# allowed host names when present. Supply a hostname, not a URL with a scheme.
vercel_url = os.environ.get("VERCEL_URL")

if vercel_url and vercel_url not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(vercel_url)


# These origins are for trusted cross-site POSTs protected by CSRF middleware.
# With no configured origins, Django accepts only its normal same-origin rules.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS", ""
    ).split(",")
    if origin.strip()
]


# Application definition

# Project apps use the apps.<name> import path because they are grouped under
# the repository's apps/ package; Django's built-in apps provide shared features.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.crops',
    'apps.customers',
    'apps.dashboard',
    'apps.harvests',
    'apps.sales',
    'apps.testing',
]

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        # Search the shared templates/ folder as well as app-level templates
        # enabled by APP_DIRS below.
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Make request, signed-in user, and flash messages available
                # to templates; the final processor adds account_role_display.
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.accounts.context_processors.account_role',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'




# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases


import dj_database_url


# Hosted Vercel deployments pass a single DATABASE_URL. SSL is required for
# that connection. Connection lifetime is set to zero; the deployment checklist
# identifies Vercel as the target, but does not explain this specific choice.
# NOTE: Confirm the intended connection-lifetime policy before changing it.
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Production: connect to Neon through its connection URL.
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "60")),
            conn_health_checks=True,
            disable_server_side_cursors=True,
            ssl_require=True,
        )
    }
else:
    # Local development: use your existing local PostgreSQL database.
    # Without DATABASE_URL, use the local PostgreSQL settings supplied by
    # DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, and DB_PORT. No SQLite fallback or
    # useful local connection defaults are configured here.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT"),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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

# Protected views send anonymous users here. A successful login goes to the
# dashboard unless a safe `next` destination was requested. Logout returns to
# login after its POST clears the session.
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Aware datetimes are always stored as UTC in the database. TIME_ZONE controls
# what "today" means and how times are displayed. Harvest windows, reminders and
# the dashboard all compare calendar dates, so this must be the farm's own zone.
# Override with DJANGO_TIME_ZONE if needed.
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Africa/Dar_es_Salaam")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

# 1. The URL prefix used to access static files in the browser (e.g., /static/css/style.css)
# Django finds static files under STATICFILES_DIRS; collectstatic copies them
# to STATIC_ROOT for deployment.
STATIC_URL = 'static/'

# 2. Additional root-level directories where Django looks for static files during development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Destination for collected static files during deployment.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Dashboard and reminders
# --------------------------------------------------------------------------

# How often (seconds) an open dashboard tab quietly re-checks for changes. The
# tab pauses while hidden. This is polling rather than WebSockets because the
# site runs on serverless functions that cannot keep a connection open.
DASHBOARD_REFRESH_SECONDS = int(os.environ.get("DASHBOARD_REFRESH_SECONDS", "60"))

# A harvest window counts as "coming up" this many days ahead in the daily
# email digest.
HARVEST_REMINDER_LEAD_DAYS = int(os.environ.get("HARVEST_REMINDER_LEAD_DAYS", "3"))

# Orders still unpaid this many days after the order date appear in the email
# digest. (The dashboard always lists every unpaid order.)
PAYMENT_REMINDER_AFTER_DAYS = int(os.environ.get("PAYMENT_REMINDER_AFTER_DAYS", "7"))

# Public base URL used for links inside reminder emails, e.g.
# "https://your-domain.example". Emails omit links when it is not set.
SITE_URL = os.environ.get("DJANGO_SITE_URL", "").rstrip("/")

# Shared secret that authorises the scheduled digest endpoint. Vercel Cron sends
# it as "Authorization: Bearer <CRON_SECRET>". When unset the endpoint refuses
# every request.
CRON_SECRET = os.environ.get("CRON_SECRET", "")

# Email: set EMAIL_HOST (plus the related variables) to send real mail. Without
# EMAIL_HOST, messages are printed to the server log so nothing is sent by
# accident during development.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_TIMEOUT = 8  # stay well inside a serverless function's time limit
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Farm System <no-reply@localhost>")
