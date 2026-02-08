# ==============================================================================
# STAGE 1: Base - Definições globais de Runtime
# ==============================================================================
FROM python:3.11-slim AS base

# Centralizamos as variáveis de ambiente que afetam todos os estágios
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Define onde o uv criará/procurará o venv
    VIRTUAL_ENV=/app/.venv \
    # Adiciona o venv ao PATH globalmente
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Dependências de execução (Runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ==============================================================================
# STAGE 2: Installer - Compilação (Onde o GCC mora)
# ==============================================================================
FROM base AS installer

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    build-essential

COPY pyproject.toml uv.lock ./
# Primeiro instala as dependências (camada pesada que muda pouco)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --all-extras

# Depois copia o código (camada leve que muda muito)
COPY . .
# Sincroniza o projeto SEM dependency groups (produção)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-extras

# ==============================================================================
# STAGE 3: Development - Com dependências opcionais (zealot, etc)
# ==============================================================================
FROM installer AS development

# Instala dependências opcionais de dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-extras

ENV DJANGO_DEBUG=True
# O PATH e código já foram herdados do installer!

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================================================
# STAGE 4: Production - A imagem final enxuta
# ==============================================================================
FROM base AS production

# Copiar venv primeiro (muda raramente = melhor cache)
COPY --from=installer /app/.venv /app/.venv

# Depois copiar código (muda frequentemente)
COPY . .

RUN python manage.py collectstatic --noinput && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
