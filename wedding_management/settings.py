"""
Configurações do projeto Django Wedding Management.

Gerado por 'django-admin startproject' usando Django 5.2.3.
"""

import logging
import logging.handlers
import os
from pathlib import Path

from django.contrib.messages import constants as messages

# Caminho base do projeto (usado para construir outros caminhos)
BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança e depuração

# Chave secreta usada para criptografia — deve ser protegida em produção
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-j_($whzy=qpta^)*1cw6&51$$dv2+(e(@g@a)q%)7*^9nq39(r",
)

# Modo debug (não usar True em produção)
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Domínios permitidos para o servidor
ALLOWED_HOSTS: list[str] = (
    os.getenv("ALLOWED_HOSTS", "").split(",") if not DEBUG else []
)

# Aplicativos instalados

INSTALLED_APPS = [
    # Aplicativos padrão do Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplicativos de terceiros
    "django_htmx",
    # "django_extensions",
    "rest_framework",
    "debug_toolbar",
    # Aplicativos do projeto
    "apps.scheduler",
    "apps.contracts",
    "apps.items",
    "apps.budget",
    "apps.pages",
    "apps.users",
    "apps.weddings",
    "apps.core",
]

# Middlewares

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",  # Suporte para requisições htmx
]

# URLs e templates

ROOT_URLCONF = "wedding_management.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Diretório global de templates
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

# Banco de dados

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Banco padrão
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Validação de senhas

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Autenticação e redirecionamentos

LOGIN_REDIRECT_URL = "weddings:my_weddings"
LOGOUT_REDIRECT_URL = "users:login"
LOGIN_URL = "/usuario/login/"
AUTH_USER_MODEL = "users.User"

# Internacionalização

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Configurações de E-mail

# Para testes locais (imprime e-mails na consola)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# (Para produção, usarias SMTP, ex: SendGrid, Amazon SES, etc.)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = '...'

# Define os e-mails que a tua view vai usar
DEFAULT_FROM_EMAIL = "contato@simaceito.com.br"  # O e-mail que "envia"
ADMIN_EMAIL = "teu-email-admin@gmail.com"  # O e-mail que "recebe"


# --- INÍCIO DA CONFIGURAÇÃO DE LOGGING ---

# Apps que terão logs separados
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

# Cria as pastas de logs (ex: /logs/scheduler/, /logs/core/)
LOGS_DIR = BASE_DIR / "logs"
for app in APP_LOGS:
    (LOGS_DIR / app).mkdir(parents=True, exist_ok=True)

# Define o nível do console baseado no modo DEBUG
CONSOLE_LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # === FORMATTERS ===
    "formatters": {
        # Formato para o Terminal (colorido)
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[%(levelname)s]%(reset)s %(asctime)s — %(name)s — %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        # Formato para Arquivos (sem cor, mais detalhes)
        "verbose": {
            "format": "[%(levelname)s] %(asctime)s — %(name)s (%(pathname)s:%(lineno)d) — %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Formato padrão do django
        "django_server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(asctime)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    # === HANDLERS ===
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "color",
            "level": CONSOLE_LOG_LEVEL,  # Nível dinâmico
        },
        "console_server": {
            "class": "logging.StreamHandler",
            "formatter": "django_server",
            "level": "INFO",
        },
    },
    # === LOGGERS ===
    "loggers": {
        # Logs padrão do Django (ex: requisições HTTP)
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Evita poluir o console com logs DEBUG do Django
            "propagate": True,
        },
        # Logs de requisições do Django (para capturar 5XX, 4XX)
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",  # Só loga erros sérios de requisição
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console_server"],  # <-- Usa o handler NÃO colorido
            "level": "INFO",
            "propagate": False,  # <-- IMPEDE que ele use o handler "console" colorido
        },
    },
}

# === CRIAÇÃO DINÂMICA DE HANDLERS E LOGGERS ===
for app in APP_LOGS:
    # Handler: Define um arquivo de log rotativo para cada app
    LOGGING["handlers"][f"file_{app}"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOGS_DIR / f"{app}/app.log",
        "formatter": "verbose",
        "encoding": "utf-8",
        "level": "DEBUG",  # Captura TUDO (debug, info, warning...) no arquivo
        "maxBytes": 5 * 1024 * 1024,  # 5 MB por arquivo
        "backupCount": 5,  # Mantém 5 arquivos de backup (app.log.1, ... .5)
    }

    # Logger: Define o logger para cada app
    LOGGING["loggers"][app] = {
        "handlers": ["console", f"file_{app}"],  # Envia para o console E para o arquivo
        "level": "DEBUG",  # O nível do logger principal do app
        "propagate": False,  # Impede que o log seja enviado duas vezes
    }

# --- FIM DA CONFIGURAÇÃO DE LOGGING ---


# Arquivos estáticos e de mídia

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Configurações gerais

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Estilo de mensagens (Bootstrap)

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# Para o Django Debug Toolbar

INTERNAL_IPS = [
    "127.0.0.1",
]
