SHELL := /bin/bash

# ==============================================================================
# CONFIGURAÇÕES E VARIÁVEIS
# ==============================================================================
DC := docker compose
EXEC_BACK := $(DC) exec backend
PYTHON := python manage.py
DJANGO_SETTINGS_MODULE := config.settings.development
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

.PHONY: help setup

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

setup: env-setup rebuild
	@echo "✨ Setup completo! Criando superusuário..."
	$(MAKE) superuser

include docker.mk
include backend.mk
include quality.mk
include production.mk
include utils.mk
