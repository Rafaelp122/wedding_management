# ==============================================================================
# STAGE 1: Base - Definições globais de Runtime
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
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ==============================================================================
# STAGE 2: Installer - Preparação da imagem de PRODUÇÃO
# ==============================================================================
FROM base AS installer

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    build-essential

COPY pyproject.toml uv.lock ./

# MUDANÇA: Adicionamos --no-dev para garantir que a venv de base seja leve
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --all-extras

COPY . .

# Sincroniza o projeto final para produção (sem ferramentas de teste/dev)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --all-extras

# ==============================================================================
# STAGE 3: Development - Imagem com Pytest, Factories e ferramentas de Dev
# ==============================================================================
FROM installer AS development

# Aqui o uv sync (sem --no-dev) instala o grupo [dependency-groups] dev
# Isso traz o pytest-factoryboy, pytest-env, etc.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-extras

ENV DJANGO_DEBUG=True
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================================================
# STAGE 4: Production - Imagem final para o Cloud Run
# ==============================================================================
FROM base AS production

# Copia a venv limpa (sem dev dependencies) do installer
COPY --from=installer /app/.venv /app/.venv
COPY . .

# Coleta estáticos e ajusta permissões
RUN python manage.py collectstatic --noinput && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
