SHELL := /bin/bash

# ==============================================================================
# CONFIGURAÇÕES E VARIÁVEIS
# ==============================================================================
DC := docker compose
EXEC_BACK := $(DC) exec backend
PYTHON := python manage.py
DJANGO_SETTINGS_MODULE := config.settings.development
# Otimização do BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

.PHONY: help setup up dev logs build rebuild down clean frontend-refresh-deps migrate makemigrations superuser shell reqs back-install openapi orval sync-api test test-cov lint mypy format check check-backend check-frontend check-ci env-setup secret-key fix-perms prod-build prod-up prod-migrate prod-shell
# Default target
help:
	@echo "=========================================================================="
	@echo "  💍 Wedding Management - Sistema de Gestão de Casamentos (NINJA EDITION)"
	@echo "=========================================================================="
	@echo ""
	@echo "📦 DOCKER & ORQUESTRAÇÃO"
	@echo "  make setup               - 🚀 Setup completo (env + rebuild + superuser)"
	@echo "  make up                  - Inicia containers e aplica migrations"
	@echo "  make dev                 - 🔥 Modo desenvolvimento (watch + logs)"
	@echo "  make logs                - Exibe logs dos serviços"
	@echo "  make down                - Para e remove todos os containers"
	@echo "  make build               - Reconstrói e inicia os containers"
	@echo "  make rebuild             - ⚠️  Destrói TUDO (DB, venv, volumes) e reconstrói do zero"
	@echo "  make clean               - Limpeza total (containers, volumes, redes)"
	@echo ""
	@echo "🐍 BACKEND (Django Ninja)"
	@echo "  make migrate             - Aplica migrações no banco de dados"
	@echo "  make makemigrations      - Gera migrations (todos apps auto-detectados)"
	@echo "  make superuser           - Cria usuário administrativo"
	@echo "  make shell               - Acessa shell interativo do Django"
	@echo "  make reqs                - Atualiza uv.lock (Crucial após mudar dependências)"
	@echo "  make back-install        - Instala pacote Python (pkg=nome)"
	@echo ""
	@echo "⚛️  FRONTEND & API SYNC"
	@echo "  make frontend-refresh-deps - ♻️  Recria frontend e sincroniza node_modules"
	@echo "  make sync-api            - 🔄 Gera OpenAPI + Hooks do Orval (Frontend)"
	@echo "  make openapi             - Gera o arquivo openapi.json a partir do Ninja"
	@echo "  make orval               - Gera os hooks do frontend (Requer openapi.json)"
	@echo ""
	@echo "🚀 PRODUÇÃO"
	@echo "  make prod-build          - Build da imagem de produção"
	@echo "  make prod-up             - Sobe container de produção"
	@echo "  make prod-migrate        - Executa migrations em produção"
	@echo "  make prod-shell          - Shell no container de produção"
	@echo ""
	@echo "🧹 QUALIDADE & MANUTENÇÃO"
	@echo "  make check-backend       - ✅ Lint + mypy + testes + openapi (backend)"
	@echo "  make check-frontend      - ✅ Lint + type-check + testes (frontend)"
	@echo "  make check-ci            - ✅ Gate local espelhando CI"
	@echo "  make check               - Alias para make check-backend"
	@echo "  make test                - Executa testes com pytest"
	@echo "  make test-cov            - Executa testes com cobertura"
	@echo "  make lint                - Analisa código com Ruff"
	@echo "  make mypy                - Valida tipagem estática no backend"
	@echo "  make format              - Formata código com Ruff"
	@echo "=========================================================================="

# ============================================================================
# Docker Commands
# ============================================================================

setup: env-setup rebuild
	@echo "✨ Setup completo! Criando superusuário..."
	$(MAKE) superuser

up:
	@echo "🚀 Iniciando containers..."
	$(DC) up -d
	$(EXEC_BACK) $(PYTHON) migrate
	@echo "✅ Pronto!"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Backend:  http://localhost:8000/api/v1/docs"

dev:
	$(DC) up -d
	$(EXEC_BACK) $(PYTHON) migrate
	$(DC) logs -f

logs:
	$(DC) logs -f

build:
	@echo "🔨 Reconstruindo e iniciando..."
	$(DC) up --build -d
	$(EXEC_BACK) $(PYTHON) migrate

rebuild:
	@echo "⚠️  Destruindo containers, volumes e redes..."
	$(DC) down -v
	@echo "🔨 Reconstruindo do zero..."
	$(DC) up --build -d
	@echo "⏳ Aguardando banco de dados..."
	@until $(DC) exec db pg_isready -U $${DB_USER:-wedding_user} -d $${DB_NAME:-wedding_db} 2>/dev/null; do sleep 2; done
	$(EXEC_BACK) $(PYTHON) migrate
	@echo "✅ Rebuild completo!"

frontend-refresh-deps:
	@echo "♻️  Recriando frontend com node_modules limpo..."
	$(DC) up -d --force-recreate --renew-anon-volumes frontend
	@echo "📦 Sincronizando dependências do frontend no container..."
	$(DC) exec frontend npm install
	@echo "✅ Dependências do frontend sincronizadas com sucesso!"

down:
	$(DC) down

clean:
	$(DC) down -v
	docker system prune -f

# ============================================================================
# Backend Commands (Django Ninja) - Desenvolvimento
# ============================================================================

migrate:
	$(EXEC_BACK) $(PYTHON) migrate

makemigrations:
	$(EXEC_BACK) $(PYTHON) makemigrations

superuser:
	$(EXEC_BACK) $(PYTHON) createsuperuser

shell:
	$(EXEC_BACK) $(PYTHON) shell

reqs:
	$(EXEC_BACK) uv lock
	@echo "✅ uv.lock atualizado no container!"

back-install:
	@if [ -z "$(pkg)" ]; then echo "❌ Erro: Use make back-install pkg=nome"; exit 1; fi
	$(EXEC_BACK) uv add "$(pkg)"
	@echo "✅ $(pkg) instalado. Rode 'make build' se o container não atualizar."

# ============================================================================
# Quality, Testing & API Sync (Orval)
# ============================================================================

openapi:
	@echo "📝 Gerando schema OpenAPI a partir do Django Ninja..."
	cd backend && uv run python manage.py export_openapi_schema --api config.api.api --output ../openapi.json --settings=$(DJANGO_SETTINGS_MODULE)
	@echo "✅ openapi.json gerado na raiz do projeto."

orval:
	@echo "📦 Gerando hooks do Orval para o Frontend..."
	cd frontend && npm run generate:api

sync-api: openapi orval
	@echo "🔄 API e Frontend sincronizados com sucesso!"

test:
	$(EXEC_BACK) uv run pytest -v

test-cov:
	$(EXEC_BACK) uv run pytest --cov=apps --cov-report=term -v

lint:
	$(EXEC_BACK) uv run ruff check .

mypy:
	$(EXEC_BACK) uv run mypy . --show-error-codes --no-color-output

format:
	$(EXEC_BACK) uv run ruff format .
	$(EXEC_BACK) uv run ruff check . --fix

check-backend: lint mypy test openapi
	@echo "✅ Pipeline de qualidade do backend passou!"

check-frontend:
	cd frontend && npm ci && npm run lint && npm run type-check && npm test
	@echo "✅ Pipeline de qualidade do frontend passou!"

check-ci: check-backend check-frontend
	@echo "✅ Gate local espelhando CI passou!"

check: check-backend

# ============================================================================
# Produção
# ============================================================================

prod-build:
	@echo "🏗️  Build da imagem de produção..."
	cd backend && docker build --target production --build-arg BUILD_SECRET_KEY=dummy-build-key-not-for-runtime -t wedding-backend:prod .

prod-up:
	@echo "🚀 Iniciando produção (HTTP local, SSL desativado)..."
	docker run -d \
		--name wedding_backend_prod \
		--env-file .env \
		-e DJANGO_SETTINGS_MODULE=config.settings.production \
		-e SECURE_SSL_REDIRECT=False \
		-p 8000:8000 \
		wedding-backend:prod

prod-migrate:
	@echo "🔄 Aplicando migrations em produção..."
	docker exec wedding_backend_prod python manage.py migrate

prod-shell:
	docker exec -it wedding_backend_prod python manage.py shell

# ============================================================================
# Utilities
# ============================================================================

env-setup:
	@if [ ! -f .env ]; then cp .env.example .env; fi

secret-key:
	@python3 generate_secret_key.py

fix-perms:
	sudo chown -R $$USER:$$USER .
