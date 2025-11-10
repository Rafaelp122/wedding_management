"""
Configurações do projeto Django Wedding Management.

Gerado por 'django-admin startproject' usando Django 5.2.3.
"""

from pathlib import Path
from django.contrib.messages import constants as messages
import os

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
ALLOWED_HOSTS: list[str] = os.getenv("ALLOWED_HOSTS", "").split(",") if not DEBUG else []

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
    "django_extensions",

    # Aplicativos do projeto
    "apps.scheduler",
    "apps.contracts",
    "apps.items",
    "apps.budget",
    "apps.pages",
    "apps.users",
    "apps.client",
    "apps.supplier",
    "apps.weddings",
    "apps.core",
]

# Autenticação e redirecionamentos

LOGIN_REDIRECT_URL = "weddings:my_weddings"
LOGOUT_REDIRECT_URL = "users:login"
LOGIN_URL = "/usuario/login/"
AUTH_USER_MODEL = "users.User"

# Middlewares

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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
        "ENGINE": "django.db.backends.sqlite3",  # Banco padrão (simples e local)
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Validação de senhas

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internacionalização

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

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
