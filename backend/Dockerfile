# ==============================================================================
# STAGE 1: Base - Configurações comuns
# ==============================================================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instala apenas o essencial para runtime (com cache mount do BuildKit)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5

# Copia o UV do binário oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ==============================================================================
# STAGE 2: Builder - Instala dependências
# ==============================================================================
FROM base AS builder

# Instala dependências de COMPILAÇÃO (com cache mount do BuildKit)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev

# Copia arquivos de dependências (pyproject.toml + uv.lock)
COPY pyproject.toml uv.lock ./

# Exporta requirements do uv.lock e instala no sistema (mais compatível com Docker)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv export --frozen --no-dev --no-hashes > /tmp/requirements.txt && \
    uv pip install --system --no-cache -r /tmp/requirements.txt

# ==============================================================================
# STAGE 3: Development - Herda do BASE (mais leve que builder)
# ==============================================================================
FROM base AS development

ENV DJANGO_DEBUG=True

# Copia apenas os pacotes Python instalados (não copia gcc, libpq-dev)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ==============================================================================
# STAGE 4: Production - Imagem final limpa
# ==============================================================================
FROM base AS production

# Copia apenas os pacotes instalados do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Coleta estáticos e ajusta permissões
RUN mkdir -p /app/staticfiles /app/media && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
# Dica: Use uma variável de ambiente para o número de workers se possível
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
