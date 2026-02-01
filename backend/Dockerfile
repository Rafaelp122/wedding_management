# Estágio Base: Comum para desenvolvimento e produção
FROM python:3.11-slim AS base

# Configurações de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala dependências do sistema necessárias para o Postgres
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio de Desenvolvimento (Alvo atual)
FROM base AS development
# O código será sincronizado via Compose Watch, mas copiamos para integridade
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Estágio de Produção (Para uso futuro)
FROM base AS production
RUN pip install --no-cache-dir gunicorn
COPY . .
RUN mkdir -p /app/staticfiles
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]