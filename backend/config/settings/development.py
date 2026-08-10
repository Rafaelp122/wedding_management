"""
Development settings: DEBUG=True, django-zeal, console email, colored logging.
"""

import socket
from urllib.parse import urlparse

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

# --- Cache & Task Queue Configuration (Valkey / Redis DB 1 & DB 0 com Fallback) ---
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379")


def _is_redis_available(url: str) -> bool:
    """Verifica se o servidor Redis está acessível via socket em dev/E2E."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        with socket.create_connection((host, port), timeout=0.3):
            return True
    except (OSError, ValueError):
        return False


if _is_redis_available(REDIS_URL):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": f"{REDIS_URL}/1",
        }
    }
    HUEY = {
        "huey_class": "huey.PriorityRedisHuey",
        "name": "wedding_tasks",
        "connection": {
            "url": f"{REDIS_URL}/0",
        },
        "immediate": env.bool("HUEY_IMMEDIATE", default=False),
        "consumer": {
            "workers": 2,
            "worker_type": "thread",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "dev-fallback-cache",
        }
    }
    HUEY = {
        "huey_class": "huey.MemoryHuey",
        "name": "dev_tasks",
        "immediate": True,
    }


# Afrouxa limites de throttling em desenvolvimento para viabilizar
# testes E2E concorrentes
NINJA_EXTRA["THROTTLE_RATES"] = {
    "auth_register": "1000/m",
    "auth_login": "1000/m",
    "auth_refresh": "1000/m",
    "auth_verify": "1000/m",
    "auth_google": "1000/m",
    "auth_password_reset_request": "1000/m",  # pragma: allowlist secret
    "auth_password_reset_confirm": "1000/m",  # pragma: allowlist secret
    "auth_verify_email_token": "1000/m",  # pragma: allowlist secret
    "auth_resend_verification": "1000/m",  # pragma: allowlist secret
}
