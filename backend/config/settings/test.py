"""
Test settings: in-memory SQLite, fast password hashers, disabled zeal.
"""

from .base import *


DEBUG = False
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
