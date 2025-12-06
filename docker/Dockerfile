# --- STAGE 1: Builder ---
# Usamos uma imagem temporária para compilar tudo
FROM python:3.12-slim as builder

WORKDIR /app

# Variáveis para evitar arquivos desnecessários no build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala dependências de BUILD (gcc, headers, etc)
# Note: --no-install-recommends evita instalar pacotes extras "sugeridos"
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Prepara o virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements/ /app/requirements/

# Instala as libs no virtualenv
RUN pip install --upgrade pip && \
    pip install -r requirements/production.txt

# --- STAGE 2: Runtime ---
# Imagem final limpa, sem gcc, sem headers
FROM python:3.12-slim as runtime

WORKDIR /app

# Variáveis de runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Instala APENAS dependências de RUNTIME (bibliotecas compartilhadas)
# libpq-dev vira libpq5, gcc sai fora
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libcairo2 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia o virtualenv pronto do estágio builder
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação
COPY . /app/

# Configura permissões e diretórios
RUN mkdir -p /app/staticfiles /app/media && \
    # O collectstatic deve ser cauteloso aqui.
    # Se ele precisar de DB connection ou env vars secretas, vai falhar no build.
    # O ideal é rodar isso no Entrypoint ou CI/CD, mas se for self-contained, ok.
    # python manage.py collectstatic --noinput --settings=wedding_management.settings.production || true && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Usamos o caminho absoluto do gunicorn dentro do venv
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "wedding_management.wsgi:application"]
