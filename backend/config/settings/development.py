"""
Development settings: DEBUG=True, django-zeal, console email, colored logging.
"""

from .base import *


INSTALLED_APPS += ["django_extensions"]


DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])

ENABLE_ZEAL = env.bool("ENABLE_ZEAL", default=True)

if ENABLE_ZEAL:
    INSTALLED_APPS += ["zeal"]
    MIDDLEWARE = ["zeal.middleware.zeal_middleware", *MIDDLEWARE]
    ZEAL_FAIL = env.bool("ZEAL_FAIL", default=False)
    ZEAL_LOG = True

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("DB_NAME", default=str(BASE_DIR.parent / "db.sqlite3")),
        "USER": env("DB_USER", default=""),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default=""),
        "PORT": env("DB_PORT", default=""),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "contato@weddingmanagement.com"
ADMIN_EMAIL = "admin@weddingmanagement.com"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "apps.core.logging.RequestIDFilter",
        },
    },
    "formatters": {
        "pretty": {
            "format": (
                "[\033[1;32m%(asctime)s\033[0m] %(levelname)s "
                "[\033[1;35m%(request_id)s\033[0m] "
                "[\033[1;34m%(name)s:%(funcName)s\033[0m] %(message)s"
            ),
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "pretty",
            "filters": ["request_id"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "wedding_management": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "urllib3": {"level": "WARNING"},
    },
}

# --- Cache Configuration ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "development-cache",
    }
}

# Afrouxa limites de throttling em desenvolvimento para viabilizar
# testes E2E concorrentes
NINJA_EXTRA["THROTTLE_RATES"] = {
    "auth_register": "1000/m",
    "auth_login": "1000/m",
    "auth_refresh": "1000/m",
    "auth_verify": "1000/m",
    "auth_google": "1000/m",
}
