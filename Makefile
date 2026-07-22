SHELL := /bin/bash

# ==============================================================================
# CONFIGURAÇÕES E VARIÁVEIS DO DOCKER
# ==============================================================================
DC := docker compose
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Autodetect: Se o container 'wedding_backend' estiver rodando, usa 'exec'.
# Caso contrário, usa 'run --rm' para criar um container temporário.
IS_RUNNING := $(shell $(DC) ps --status running --format json 2>/dev/null | grep backend)
ifeq ($(strip $(IS_RUNNING)),)
    RUN_BACK := $(DC) run --rm backend
else
    RUN_BACK := $(DC) exec backend
endif

.PHONY: help setup up dev logs down build rebuild clean db-reset back-logs front-logs \
        frontend-dev landing-dev sync-api openapi orval frontend-test frontend-test-changed \
        migrate makemigrations superuser shell reqs back-install \
        test test-cov lint mypy format check-backend check-frontend check-landing check-ci check \
        prod-build prod-up prod-migrate prod-shell \
        env-setup secret-key fix-perms

# ==============================================================================
# MENU DE AJUDA (HELP)
# ==============================================================================
help:
	@echo "=========================================================================="
	@echo "  💍 Wedding Management - Sistema de Gestão de Casamentos (NINJA EDITION)"
	@echo "=========================================================================="
	@echo ""
	@echo "📦 DOCKER & ORQUESTRAÇÃO (Ambiente de Dev)"
	@echo "  make setup               - 🚀 Setup completo (env + rebuild + superuser)"
	@echo "  make up                  - Inicia containers de backend/banco e aplica migrations"
	@echo "  make dev                 - 🔥 Dev: sobe containers de backend/banco + segue os logs"
	@echo "  make build               - 🔨 Dev: reconstrói imagens e reinicia containers"
	@echo "  make rebuild             - ⚠️  Destrói TUDO (volumes, DB) e reconstrói do zero"
	@echo "  make down                - Para e remove todos os containers"
	@echo "  make clean               - Limpeza de imagens antigas e volumes"
	@echo "  make db-reset            - ⚠️  Apaga e recria o banco de dados (rápido)"
	@echo "  make back-logs           - Segue os logs do container backend"
	@echo "  make front-logs          - Segue os logs do container frontend (se ativo)"
	@echo ""
	@echo "🐍 BACKEND (Django Ninja via Container/Host wrapper)"
	@echo "  make migrate             - Aplica migrações no banco de dados"
	@echo "  make makemigrations      - Gera migrations"
	@echo "  make superuser           - Cria usuário administrativo"
	@echo "  make shell               - Acessa shell interativo do Django"
	@echo "  make reqs                - Atualiza uv.lock (Crucial após mudar dependências)"
	@echo "  make back-install        - Instala pacote Python (pkg=nome)"
	@echo ""
	@echo "⚛️  FRONTEND & LANDING PAGE (Rodando no Host)"
	@echo "  make frontend-dev        - 🔥 Vite dev server local (fora do Docker - evita conflito)"
	@echo "  make landing-dev         - 🔥 Astro dev server local (fora do Docker)"
	@echo "  make sync-api            - 🔄 Sincroniza API: gera OpenAPI + Hooks do Orval"
	@echo "  make openapi             - Gera openapi.json a partir do container backend"
	@echo "  make orval               - Gera os hooks do frontend a partir do openapi.json"
	@echo ""
	@echo "🚀 PRODUÇÃO"
	@echo "  make prod-build          - Build da imagem de produção"
	@echo "  make prod-up             - Sobe container de produção localmente"
	@echo "  make prod-migrate        - Executa migrations em produção"
	@echo "  make prod-shell          - Shell no container de produção"
	@echo ""
	@echo "🧹 QUALIDADE & MANUTENÇÃO"
	@echo "  make check-backend       - ✅ Executa lint + mypy + testes + openapi (backend)"
	@echo "  make check-frontend      - ✅ Executa lint + type-check + testes + build prod (frontend)"
	@echo "  make check-landing       - ✅ Executa lint + build prod (landing)"
	@echo "  make check-ci            - ✅ Gate local completo de CI"
	@echo "  make check               - Alias para check-backend"
	@echo "  make test                - Executa testes com pytest"
	@echo "  make test-cov            - Executa testes com cobertura"
	@echo "  make lint                - Analisa código com Ruff"
	@echo "  make mypy                - Valida tipagem estática no backend"
	@echo "  make format              - Formata código com Ruff"
	@echo "  make secret-key          - Gera uma nova SECRET_KEY"
	@echo "  make fix-perms           - Ajusta permissões dos arquivos do projeto"
	@echo "=========================================================================="

# ==============================================================================
# 📦 DOCKER & ORQUESTRAÇÃO
# ==============================================================================
setup: env-setup rebuild
	@echo "✨ Setup completo! Criando superusuário..."
	$(MAKE) superuser

up:
	@echo "🚀 Iniciando containers essenciais (db e backend)..."
	$(DC) up -d db backend
	@echo "⏳ Aguardando banco de dados estar pronto..."
	@until $(DC) exec db pg_isready -U $${DB_USER:-wedding_user} -d $${DB_NAME:-wedding_db} >/dev/null 2>&1; do sleep 1; done
	$(MAKE) migrate
	@echo "✅ Backend pronto!"
	@echo "   Docs/API:  http://localhost:8000/api/v1/docs"

dev:
	$(DC) up -d db backend
	@echo "⏳ Aguardando banco de dados estar pronto..."
	@until $(DC) exec db pg_isready -U $${DB_USER:-wedding_user} -d $${DB_NAME:-wedding_db} >/dev/null 2>&1; do sleep 1; done
	$(MAKE) migrate
	$(DC) logs -f backend db

build:
	@echo "🔨 Reconstruindo imagens de dev..."
	$(DC) up --build -d db backend
	@echo "⏳ Aguardando banco de dados estar pronto..."
	@until $(DC) exec db pg_isready -U $${DB_USER:-wedding_user} -d $${DB_NAME:-wedding_db} >/dev/null 2>&1; do sleep 1; done
	$(MAKE) migrate

rebuild:
	@echo "⚠️  Destruindo containers, volumes e redes..."
	$(DC) down -v
	@echo "🔨 Reconstruindo do zero..."
	$(DC) up --build -d db backend
	@echo "⏳ Aguardando banco de dados estar pronto..."
	@until $(DC) exec db pg_isready -U $${DB_USER:-wedding_user} -d $${DB_NAME:-wedding_db} >/dev/null 2>&1; do sleep 1; done
	$(MAKE) migrate
	@echo "✅ Rebuild completo!"

down:
	$(DC) down

clean:
	$(DC) down -v
	@echo "🧹 Limpando cache do docker..."
	docker image prune -f

db-reset:
	@echo "⚠️  ATENÇÃO: Apagando todos os dados do banco..."
	$(DC) down -v db
	$(DC) up -d db
	@echo "⏳ Aguardando banco de dados estar pronto..."
	@until $(DC) exec db pg_isready -U $${DB_USER:-wedding_user} -d $${DB_NAME:-wedding_db} >/dev/null 2>&1; do sleep 1; done
	$(MAKE) migrate
	@echo "✅ Banco de dados resetado com sucesso!"

back-logs:
	$(DC) logs -f backend

front-logs:
	$(DC) logs -f frontend

# ==============================================================================
# ⚛️ FRONTEND & LANDING PAGE (Host)
# ==============================================================================
frontend-dev:
	@echo "🔥 Iniciando Vite dev server local..."
	cd frontend && pnpm run dev

landing-dev:
	@echo "🔥 Astro dev server local..."
	cd landing && pnpm run dev

openapi:
	@echo "📝 Gerando schema OpenAPI a partir do Django Ninja..."
	$(RUN_BACK) make openapi
	@# Move o openapi.json gerado do volume backend para a raiz do host
	@mv backend/openapi.json ./openapi.json
	@echo "✅ openapi.json atualizado na raiz."

orval:
	@echo "📦 Gerando hooks do Orval..."
	cd frontend && pnpm run generate:api

sync-api: openapi orval
	@echo "🔄 API e Frontend sincronizados!"

frontend-test:
	@echo "🧪 Executando todos os testes do frontend..."
	cd frontend && pnpm test

frontend-test-changed:
	@echo "🧪 Executando testes do frontend modificados no Git..."
	cd frontend && pnpm exec vitest run --changed

frontend-e2e:
	@echo "🔄 Preparando banco de dados para testes E2E..."
	$(RUN_BACK) python manage.py flush --noinput
	$(RUN_BACK) python manage.py seed_db
	@echo "🧪 Executando testes E2E com Playwright..."
	cd frontend && pnpm exec playwright test --workers=1

frontend-e2e-report:
	@echo "📊 Abrindo o relatório de testes E2E do Playwright..."
	cd frontend && pnpm exec playwright show-report

# ==============================================================================
# 🐍 COMANDOS REPASSADOS PARA O CONTAINER
# ==============================================================================
migrate:
	$(RUN_BACK) make migrate

makemigrations:
	$(RUN_BACK) make makemigrations

superuser:
	$(RUN_BACK) make superuser

shell:
	$(RUN_BACK) make shell

reqs:
	$(RUN_BACK) make reqs

back-install:
	@if [ -z "$(pkg)" ]; then echo "❌ Erro: Use make back-install pkg=nome"; exit 1; fi
	$(RUN_BACK) make back-install pkg="$(pkg)"

test:
	$(RUN_BACK) make test

test-cov:
	$(RUN_BACK) make test-cov

lint:
	$(RUN_BACK) make lint

mypy:
	$(RUN_BACK) make mypy

format:
	$(RUN_BACK) make format

# ==============================================================================
# 🚀 PRODUÇÃO
# ==============================================================================
prod-build:
	@echo "🏗️  Build da imagem de produção..."
	cd backend && docker build --target production --build-arg BUILD_SECRET_KEY=dummy-build-key-not-for-runtime -t wedding-backend:prod . # pragma: allowlist secret

prod-up:
	@echo "🚀 Iniciando produção (HTTP local, SSL desativado)..."
	@docker rm -f wedding_backend_prod >/dev/null 2>&1 || true
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

# ==============================================================================
# 🧹 PIPELINES DE QUALIDADE & CI GATES
# ==============================================================================
check-backend:
	$(RUN_BACK) make check-backend

check-frontend:
	cd frontend && pnpm install --frozen-lockfile && pnpm run lint && pnpm run type-check && pnpm test && pnpm run build

check-landing:
	cd landing && pnpm install --frozen-lockfile && pnpm exec astro check && pnpm run build

check-ci: check-backend check-frontend check-landing
	@echo "✅ Todos os gates locais passaram com sucesso!"

check: check-backend

# ==============================================================================
# UTILS
# ==============================================================================
env-setup:
	@if [ ! -f .env ]; then cp .env.example .env; fi

secret-key:
	@python3 -c 'import secrets; print(secrets.token_urlsafe(50))'

fix-perms:
	sudo chown -R $$USER:$$USER .
