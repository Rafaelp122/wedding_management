"""
Django settings for Wedding Management project.
Development configuration.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file (local dev and Docker)
load_dotenv(BASE_DIR.parent / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-j_($whzy=qpta^)*1cw6&51$$dv2+(e(@g@a)q%)7*^9nq39(r",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
]

# Application definition
INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party apps
    "ninja",
    "ninja_jwt",
    "ninja_extra",
    "corsheaders",
    # Project apps - Core
    "apps.core",
    "apps.users",
    "apps.weddings",
    # Project apps - Dominios
    "apps.finances",
    "apps.logistics",
    "apps.scheduler",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.RequestIDMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# django-zeal para detectar N+1 queries (pode deixar a aplicação ~2x mais lenta)
ENABLE_ZEAL = os.getenv("ENABLE_ZEAL", "False") == "True"

if ENABLE_ZEAL:
    INSTALLED_APPS += ["zeal"]
    MIDDLEWARE = ["zeal.middleware.ZealotMiddleware", *MIDDLEWARE]

    # Configurações de comportamento do django-zeal
    ZEAL_FAIL = True  # Crucial para o CI: faz o teste quebrar (Error 500) se houver N+1
    ZEAL_LOG = True  # Exibe alertas no console

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

# Database - SQLite for development, PostgreSQL for Docker
DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "DB_ENGINE", os.getenv("DATABASE_ENGINE", "django.db.backends.sqlite3")
        ),
        "NAME": os.getenv(
            "DB_NAME", os.getenv("DATABASE_NAME", str(BASE_DIR.parent / "db.sqlite3"))
        ),
        "USER": os.getenv("DB_USER", os.getenv("DATABASE_USER", "")),
        "PASSWORD": os.getenv("DB_PASSWORD", os.getenv("DATABASE_PASSWORD", "")),
        "HOST": os.getenv("DB_HOST", os.getenv("DATABASE_HOST", "")),
        "PORT": os.getenv("DB_PORT", os.getenv("DATABASE_PORT", "")),
    }
}

# SQLite para usar com a interface do vscode
if "test" in sys.argv or "pytest" in sys.modules:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Authentication
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# Django Sites Framework
SITE_ID = 1

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
    ).split(",")
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# JWT Configuration
NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = "."

# Email (console for development)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "contato@weddingmanagement.com"
ADMIN_EMAIL = "admin@weddingmanagement.com"

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "apps.core.logging.RequestIDFilter",
        },
    },
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(levelname)s %(asctime)s %(request_id)s %(name)s %(module)s %(funcName)s %(message)s",  # noqa
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        },
        "pretty": {
            "format": "[\033[1;32m%(asctime)s\033[0m] %(levelname)s [\033[1;35m%(request_id)s\033[0m] [\033[1;34m%(name)s:%(funcName)s\033[0m] %(message)s",  # noqa
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "pretty" if DEBUG else "json",
            "filters": ["request_id"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "wedding_management": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "urllib3": {"level": "WARNING"},
    },
}
