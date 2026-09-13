"""
Test settings: in-memory SQLite, fast password hashers, disabled zeal.
"""

from pathlib import Path

from .base import *


DEBUG = False
TESTING = True
ALLOWED_HOSTS = ["testserver"]


ENABLE_ZEAL = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "test@wedding.com"

# --- Cache Configuration ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# --- Tasks Configuration for Testing (Synchronous In-Memory) ---
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.immediate.ImmediateBackend",
    }
}

HUEY = {
    "huey_class": "huey.MemoryHuey",
    "name": "test_tasks",
    "immediate": True,
}

MEDIA_ROOT = Path("/tmp/test_media")  # noqa: S108
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
