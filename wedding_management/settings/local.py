"""
Local development settings.
"""

import os

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Disable HTTPS redirect for local development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Database - Use PostgreSQL from Docker Compose or SQLite if not available
if os.getenv("POSTGRES_HOST"):
    # Using PostgreSQL from Docker
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "wedding_management"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres123"),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    # Using SQLite for pure local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# Debug toolbar configuration
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(  # noqa: F405
    0, "debug_toolbar.middleware.DebugToolbarMiddleware"
)
INTERNAL_IPS = [
    "127.0.0.1",
    "172.18.0.1",  # Docker gateway IP
]

# Email backend - console for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery - local Redis
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to run tasks synchronously

# Static/Media files
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405
