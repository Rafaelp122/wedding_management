"""
Base settings for Wedding Management project.
These settings are common to all environments (local, production, test).
"""

import os
import sys
from pathlib import Path

from django.contrib.messages import constants as messages

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-j_($whzy=qpta^)*1cw6&51$$dv2+(e(@g@a)q%)7*^9nq39(r",
)

# Application definition

INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required for django-allauth
    # Third-party apps
    "rest_framework",  # Django REST Framework
    "django_htmx",  # HTMX support
    # Django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Project apps
    "apps.scheduler",
    "apps.contracts",
    "apps.items",
    "apps.budget",
    "apps.pages",
    "apps.users",
    "apps.weddings",
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "wedding_management.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "wedding_management.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa: E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Authentication settings
LOGIN_REDIRECT_URL = "weddings:my_weddings"
LOGOUT_REDIRECT_URL = "/accounts/login/"
LOGIN_URL = "/accounts/login/"
AUTH_USER_MODEL = "users.User"

# Django Sites Framework (required for allauth)
SITE_ID = 1

# Django-allauth Configuration
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Allauth settings (updated for django-allauth 65+)
ACCOUNT_LOGIN_METHODS = {"email", "username"}  # Replaces ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_SESSION_REMEMBER = None
ACCOUNT_USERNAME_MIN_LENGTH = 3
# Signup fields (replaces deprecated EMAIL_REQUIRED, USERNAME_REQUIRED, SIGNUP_PASSWORD_ENTER_TWICE)
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_FORMS = {
    "signup": "apps.users.web.forms.CustomUserCreationForm",
    "login": "apps.users.web.forms.CustomLoginForm",
    "reset_password": "apps.users.web.forms.CustomResetPasswordForm",
}
ACCOUNT_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
# Padrão monetário brasileiro
USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = "."

# Email settings (default to console, override in production)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "contato@simaceito.com.br"
ADMIN_EMAIL = "admin@simaceito.com.br"

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Message tags (Bootstrap compatible)
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# Django REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": ("rest_framework.pagination.PageNumberPagination"),
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATE_FORMAT": "%Y-%m-%d",
}

# Logging configuration
APP_LOGS = [
    "apps.scheduler",
    "apps.contracts",
    "apps.items",
    "apps.budget",
    "apps.pages",
    "apps.users",
    "apps.weddings",
    "apps.core",
]

LOGS_DIR = BASE_DIR / "logs"
for app in APP_LOGS:
    (LOGS_DIR / app).mkdir(parents=True, exist_ok=True)

# Determine console log level
if "test" in sys.argv or "pytest" in sys.modules:
    CONSOLE_LOG_LEVEL = "ERROR"
elif os.getenv("DEBUG", "True").lower() in ("true", "1", "yes"):
    CONSOLE_LOG_LEVEL = "DEBUG"
else:
    CONSOLE_LOG_LEVEL = "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[%(levelname)s]%(reset)s %(asctime)s — %(name)s — %(message)s",  # noqa: E501
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "verbose": {
            "format": "[%(levelname)s] %(asctime)s — %(name)s (%(pathname)s:%(lineno)d) — %(message)s",  # noqa: E501
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "django_server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(asctime)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "color",
            "level": CONSOLE_LOG_LEVEL,
        },
        "console_server": {
            "class": "logging.StreamHandler",
            "formatter": "django_server",
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console_server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Dynamic handlers and loggers for each app
for app in APP_LOGS:
    LOGGING["handlers"][f"file_{app}"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOGS_DIR / f"{app}/app.log",
        "formatter": "verbose",
        "encoding": "utf-8",
        "level": "DEBUG",
        "maxBytes": 5 * 1024 * 1024,  # 5 MB
        "backupCount": 5,
    }

    LOGGING["loggers"][app] = {
        "handlers": ["console", f"file_{app}"],
        "level": "DEBUG",
        "propagate": False,
    }

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
