# syntax=docker/dockerfile:1

# ==============================================================================
# STAGE 1: Base - O mínimo necessário
# ==============================================================================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ==============================================================================
# STAGE 2: Builder - Apenas para compilar o venv
# ==============================================================================
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev --all-extras

# ==============================================================================
# STAGE 3: Development - O seu parquinho
# ==============================================================================
FROM builder AS development

RUN uv sync --frozen --no-install-project --all-extras


COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.development

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================================================
# STAGE 4: Production - Eficiência máxima para Cloud Run
# ==============================================================================
FROM base AS production

ARG BUILD_SECRET_KEY=dummy-secret-key-for-collectstatic-32-chars # pragma: allowlist secret

ENV DJANGO_SETTINGS_MODULE=config.settings.production

RUN useradd -m -u 1000 appuser

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

COPY --chown=appuser:appuser . .

RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=${BUILD_SECRET_KEY} \
    python manage.py collectstatic --noinput

USER appuser

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/v1/health')" || exit 1

CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080} --worker-class gthread --workers ${GUNICORN_WORKERS:-2} --threads 4 --timeout 60"]
