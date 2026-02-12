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

# Copia APENAS o necessário para instalar dependências (otimiza cache)
COPY pyproject.toml uv.lock ./

# Cria o venv de produção limpo
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --all-extras

# ==============================================================================
# STAGE 3: Development - O seu parquinho
# ==============================================================================
FROM builder AS development

# Instala as dependências de dev em cima do que já existe
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --all-extras

COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================================================
# STAGE 4: Production - Eficiência máxima para Cloud Run
# ==============================================================================
FROM base AS production

# 1. Cria o usuário primeiro
RUN useradd -m -u 1000 appuser

# 2. Copia o venv do builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# 3. Copia o código fonte
COPY --chown=appuser:appuser . .

USER appuser

# 4. Coleta estáticos (o Django está no path e o usuário tem permissão)
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
