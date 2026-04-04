SHELL := /bin/bash

# ==============================================================================
# CONFIGURAÇÕES E VARIÁVEIS
# ==============================================================================
DC := docker compose
EXEC_BACK := $(DC) exec backend
EXEC_FRONT := $(DC) exec frontend
PYTHON := python manage.py

# Detecta todos os apps dentro da pasta apps
APPS := $(shell find backend/apps -mindepth 1 -maxdepth 1 -type d ! -name '__pycache__' -exec basename {} \;)

# Habilita BuildKit para builds mais rápidos
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

.PHONY: help up dev down build rebuild clean logs restart
.PHONY: migrate makemigrations db-reset db-flush show-migrations superuser shell back-shell back-logs reqs back-install
.PHONY: front-install front-shell front-logs front-dev
.PHONY: test test-cov test-parallel lint lint-fix format check clean-cache fix-perms
.PHONY: secret-key env-setup check-env local-install setup-hooks setup sync-api openapi orval
.PHONY: local-migrate local-makemigrations local-run local-shell local-createsuperuser

# Default target
help:
	@echo "=========================================================================="
	@echo "  💍 Wedding Management - Sistema de Gestão de Casamentos (NINJA EDITION)"
	@echo "=========================================================================="
	@echo ""
	@echo "📦 DOCKER & ORQUESTRAÇÃO"
	@echo "  make setup               - 🚀 Setup completo (env + build + superuser)"
	@echo "  make up                  - Inicia containers e aplica migrations"
	@echo "  make dev                 - 🔥 Modo desenvolvimento (watch + logs)"
	@echo "  make down                - Para e remove todos os containers"
	@echo "  make build               - Reconstrói e inicia os containers"
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
	@echo "  make sync-api            - 🔄 Gera OpenAPI + Hooks do Orval (Frontend)"
	@echo "  make openapi             - Gera o arquivo openapi.json a partir do Ninja"
	@echo "  make orval               - Gera os hooks do frontend (Requer openapi.json)"
	@echo ""
	@echo "🧹 QUALIDADE & MANUTENÇÃO"
	@echo "  make check               - ✅ Roda lint + testes + openapi (CI gate)"
	@echo "  make test                - Executa testes com pytest"
	@echo "  make lint                - Analisa código com Ruff"
	@echo "  make format              - Formata código com Ruff"
	@echo "=========================================================================="

# ============================================================================
# Docker Commands
# ============================================================================

setup: env-setup build
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

build:
	@echo "🔨 Reconstruindo e iniciando..."
	$(DC) up --build -d
	$(EXEC_BACK) $(PYTHON) migrate

down:
	$(DC) down

clean:
	$(DC) down -v
	docker system prune -f

# ============================================================================
# Backend Commands (Django Ninja)
# ============================================================================

migrate:
	$(EXEC_BACK) $(PYTHON) migrate

makemigrations:
	$(EXEC_BACK) $(PYTHON) makemigrations $(APPS)

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

# O Django Ninja usa 'export_schema' em vez do spectacular
openapi:
	@echo "📝 Gerando schema OpenAPI a partir do Django Ninja..."
	$(EXEC_BACK) $(PYTHON) export_openapi_schema --api config.api.api --output ../openapi.json
	@echo "✅ openapi.json gerado na raiz do projeto."

orval:
	@echo "📦 Gerando hooks do Orval para o Frontend..."
	cd frontend && npm run generate:api

sync-api: openapi orval
	@echo "🔄 API e Frontend sincronizados com sucesso!"

test:
	$(EXEC_BACK) uv run pytest -v

lint:
	$(EXEC_BACK) uv run ruff check .

format:
	$(EXEC_BACK) uv run ruff format .
	$(EXEC_BACK) uv run ruff check . --fix

check: lint test openapi
	@echo "✅ Pipeline de qualidade passou!"

# ============================================================================
# Utilities
# ============================================================================

env-setup:
	@if [ ! -f .env ]; then cp .env.example .env; fi

secret-key:
	@python3 generate_secret_key.py

fix-perms:
	sudo chown -R $$USER:$$USER .
