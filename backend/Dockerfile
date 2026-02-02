# ==============================================================================
# STAGE 1: Base - O único lugar com APT
# ==============================================================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Unificamos o APT aqui.postgresql-client e libpq5 são leves e úteis em tudo.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ==============================================================================
# STAGE 2: Installer - Resolve tudo de uma vez
# ==============================================================================
FROM base AS installer

# Copia apenas o necessário para instalar
COPY pyproject.toml uv.lock ./

# Instala TUDO (incluindo dev) em um virtualenv dentro de /app/.venv
# O uv sync é muito mais rápido que exportar para txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# ==============================================================================
# STAGE 3: Development
# ==============================================================================
FROM installer AS development

ENV DJANGO_DEBUG=True
# Garante que o Python use o venv criado no stage anterior
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================================================
# STAGE 4: Production - A imagem "magra"
# ==============================================================================
FROM base AS production

# No lugar de instalar de novo, apenas limpamos o venv do stage installer
# ou criamos um só com prod (opcional para simplicidade)
COPY --from=installer /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN mkdir -p /app/staticfiles /app/media && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
