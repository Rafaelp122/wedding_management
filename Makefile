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

# Habilita BuildKit para builds mais rápidos e com cache
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

.PHONY: help up dev down build rebuild clean logs restart
.PHONY: migrate makemigrations db-reset db-flush show-migrations superuser shell back-shell back-logs reqs back-install
.PHONY: front-install front-shell front-logs front-dev
.PHONY: test test-cov test-parallel lint lint-fix format check clean-cache fix-perms
.PHONY: secret-key env-setup check-env local-install setup-hooks setup
.PHONY: local-migrate local-makemigrations local-run local-shell local-createsuperuser
.PHONY: data-dump data-load prune
.PHONY: test test-cov test-parallel lint lint-fix format check openapi clean-cache fix-perms

# Default target
help:
	@echo "=========================================================================="
	@echo "  💍 Wedding Management - Sistema de Gestão de Casamentos"
	@echo "=========================================================================="
	@echo ""
	@echo "📦 DOCKER & ORQUESTRAÇÃO"
	@echo "  make setup               - 🚀 Setup completo (env + build + superuser)"
	@echo "  make up                  - Inicia containers e aplica migrations"
	@echo "  make dev                 - 🔥 Modo desenvolvimento (watch + hot reload)"
	@echo "  make down                - Para e remove todos os containers"
	@echo "  make build               - Reconstrói e inicia os containers"
	@echo "  make rebuild             - Reconstrói do zero (sem cache)"
	@echo "  make clean               - Limpeza total (containers, volumes, redes)"
	@echo "  make prune               - Limpa imagens e volumes não utilizados"
	@echo "  make logs                - Exibe logs de todos os containers"
	@echo "  make restart             - Reinicia containers"
	@echo ""
	@echo "🐍 BACKEND (Django REST Framework)"
	@echo "  make migrate             - Aplica migrações no banco de dados"
	@echo "  make makemigrations      - Gera migrations (todos apps auto-detectados)"
	@echo "  make show-migrations     - Mostra status das migrações"
	@echo "  make db-reset            - ⚠️  APAGA banco e migrations, recria tudo"
	@echo "  make db-flush            - ⚠️  Limpa dados do banco (mantém tabelas)"
	@echo "  make superuser           - Cria usuário administrativo"
	@echo "  make shell               - Acessa shell interativo do Django"
	@echo "  make data-dump           - Exporta dados do banco para seed.json"
	@echo "  make data-load           - Importa dados do seed.json"
	@echo "  make back-install        - Instala pacote Python (pkg=nome)"
	@echo "  make reqs                - Atualiza uv.lock"
	@echo "  make back-shell          - Acessa terminal do container backend"
	@echo "  make back-logs           - Exibe logs do backend"
	@echo ""
	@echo "🔐 CONFIGURAÇÃO & AMBIENTE"
	@echo "  make secret-key          - Gera SECRET_KEY segura para Django"
	@echo "  make env-setup           - Configura arquivo .env (copia .env.example)"
	@echo "  make check-env           - Verifica se .env está atualizado"
	@echo "  make local-install       - Instala deps localmente (UV sync)"
	@echo "  make setup-hooks         - Instala e configura git hooks (pre-commit)"
	@echo ""
	@echo "💻 DESENVOLVIMENTO LOCAL (sem Docker)"
	@echo "  make local-migrate       - Aplica migrações localmente"
	@echo "  make local-makemigrations- Cria migrações localmente"
	@echo "  make local-run           - Inicia servidor Django local"
	@echo "  make local-shell         - Abre Django shell local"
	@echo "  make local-createsuperuser - Cria superusuário local"
	@echo "  make front-dev           - Inicia servidor Vite local"
	@echo ""
	@echo "⚛️  FRONTEND (React + Vite)"
	@echo "  make front-install       - Instala deps npm (pkg=nome para específico)"
	@echo "  make front-shell         - Acessa terminal do container frontend"
	@echo "  make front-logs          - Exibe logs do frontend"
	@echo ""
	@echo "🧹 QUALIDADE & MANUTENÇÃO"
	@echo "  make check               - ✅ Roda lint + testes + openapi (CI gate)"
	@echo "  make openapi             - 📝 Gera/Atualiza o schema openapi.json"
	@echo "  make orval               - 🚀 Gera hooks e tipos do React Query"
	@echo "  make test                - Executa testes com pytest"
	@echo "  make test-cov            - Testes com cobertura HTML"
	@echo "  make test-parallel       - Testes em paralelo (pytest-xdist)"
	@echo "  make lint                - Analisa código com Ruff"
	@echo "  make lint-fix            - Corrige problemas de lint"
	@echo "  make format              - Formata código automaticamente"
	@echo "  make clean-cache         - Limpa cache Python e temporários"
	@echo "  make fix-perms           - Corrige permissões de arquivos"
	@echo "=========================================================================="

# ============================================================================
# Docker Commands
# ============================================================================

# Setup completo: env, build, migrations e superuser
setup: env-setup build
	@echo "✨ Setup completo! Criando superusuário..."
	$(MAKE) superuser

up:
	@echo "🚀 Iniciando containers..."
	$(DC) up -d
	@echo "🔄 Aguardando banco e aplicando migrations..."
	@# O comando abaixo falhará se o container não subir, o que é melhor que o sleep
	$(EXEC_BACK) $(PYTHON) migrate
	@echo "✅ Pronto!"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Admin:    http://localhost:8000/admin"
	@echo "   Swagger:  http://localhost:8000/api/docs/"

dev:
	@echo "🔥 Iniciando modo desenvolvimento..."
	@echo "   • Hot reload automático para código Python"
	@echo "   • Para rebuild após mudar deps: make build"
	@echo ""
	$(DC) up -d
	@echo "🔄 Aguardando banco e aplicando migrations..."
	$(EXEC_BACK) $(PYTHON) migrate
	@echo "✅ Pronto! Logs em tempo real:"
	@echo ""
	$(DC) logs -f

build:
	@echo "🔨 Reconstruindo e iniciando..."
	$(DC) up --build -d
	$(EXEC_BACK) $(PYTHON) migrate

rebuild:
	@echo "� Resetando volumes e reconstruindo do zero..."
	$(DC) down -v
	$(DC) build --no-cache
	$(DC) up -d
	$(EXEC_BACK) $(PYTHON) migrate

down:
	@echo "🛑 Parando containers..."
	$(DC) down

clean:
	@echo "🧹 Limpeza total (containers, volumes, redes)..."
	$(DC) down -v
	docker system prune -f
	@echo "✅ Limpeza concluída!"

prune:
	@echo "🧹 Limpando imagens e volumes não utilizados..."
	docker system prune -a --volumes -f
	@echo "✅ SSD liberado!"

logs:
	$(DC) logs -f

restart:
	@echo "🔄 Reiniciando containers..."
	$(DC) restart

# ============================================================================
# Backend Commands
# ============================================================================

migrate:
	@echo "🔄 Aplicando migrations..."
	$(EXEC_BACK) $(PYTHON) migrate

makemigrations:
	@echo "📝 Gerando migrations para: $(APPS)"
	$(EXEC_BACK) $(PYTHON) makemigrations $(APPS)

show-migrations:
	@echo "📊 Status das migrações:"
	$(EXEC_BACK) $(PYTHON) showmigrations

db-reset:
	@echo "⚠️  ATENÇÃO: Este comando vai APAGAR o banco de dados e todas as migrations!"
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
	echo "🗑️  Parando containers..."; \
	$(DC) down -v; \
	echo "🗑️  Removendo arquivos de migration..."; \
	find backend/apps -path "*/migrations/*.py" -not -name "__init__.py" -delete; \
	find backend/apps -path "*/migrations/__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true; \
	echo "🚀 Recriando containers..."; \
	$(DC) up -d; \
	echo "📝 Gerando novas migrations (Django resolve dependências automaticamente)..."; \
	$(EXEC_BACK) $(PYTHON) makemigrations; \
	echo "✅ Aplicando migrations..."; \
	$(EXEC_BACK) $(PYTHON) migrate; \
	echo "🎉 Reset completo! Agora crie um superuser com 'make superuser'"; \
	else \
	echo "❌ Operação cancelada."; \
	fi

superuser:
	$(EXEC_BACK) $(PYTHON) createsuperuser

db-flush:
	@echo "⚠️  Limpando dados do banco (mantendo tabelas)..."
	$(EXEC_BACK) $(PYTHON) flush --noinput
	@echo "✅ Banco limpo!"

data-dump:
	@echo "📦 Exportando dados para seed.json..."
	$(EXEC_BACK) $(PYTHON) dumpdata --exclude auth.permission --exclude contenttypes > seed.json
	@echo "✅ Dados exportados!"

data-load:
	@echo "📥 Importando dados de seed.json..."
	$(EXEC_BACK) $(PYTHON) loaddata seed.json
	@echo "✅ Dados importados!"

shell:
	$(EXEC_BACK) $(PYTHON) shell

back-shell:
	$(EXEC_BACK) bash

back-logs:
	$(DC) logs -f backend

reqs:
	$(EXEC_BACK) uv lock
	@echo "✅ uv.lock atualizado!"

back-install:
	@if [ -z "$(pkg)" ]; then echo "❌ Erro: Use make back-install pkg=nome-do-pacote"; exit 1; fi
	$(EXEC_BACK) uv add "$(pkg)"
	@echo "✅ $(pkg) instalado e adicionado ao pyproject.toml"

# ============================================================================
# Frontend Commands
# ============================================================================

front-install:
	$(EXEC_FRONT) npm install $(pkg)

front-shell:
	$(EXEC_FRONT) sh

front-logs:
	$(DC) logs -f frontend

# ============================================================================
# Quality & Maintenance Commands
# ============================================================================

clean-cache:
	@echo "🧹 Limpando cache e arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf node_modules/.vite 2>/dev/null || true
	@echo "✅ Limpeza concluída!"

# ============================================================================
# Environment & Security
# ============================================================================

secret-key:
	@python3 generate_secret_key.py

env-setup:
	@echo "⚙️  Configurando arquivo .env..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Arquivo .env criado a partir de .env.example"; \
		echo "⚠️  IMPORTANTE: Execute 'make secret-key' para gerar uma SECRET_KEY segura"; \
	else \
		echo "⚠️  Arquivo .env já existe. Não foi modificado."; \
	fi

check-env:
	@echo "🔍 Verificando variáveis de ambiente..."
	@diff <(grep -v '^#' .env.example | cut -d= -f1 | sort) \
	      <(grep -v '^#' .env | cut -d= -f1 | sort) \
	      && echo "✅ .env está atualizado!" \
	      || echo "⚠️  Atenção: Existem divergências entre seu .env e o .env.example"

local-install:
	@echo "🐍 Configurando ambiente com UV..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ UV não encontrado!"; exit 1; }
	cd backend && uv sync
	uv run pre-commit install
	@echo "✅ Ambiente local pronto! Use 'uv run $(PYTHON) runserver'"

# ============================================================================
# Local Development Commands (sem Docker)
# ============================================================================

local-migrate:
	@echo "📦 Aplicando migrações localmente..."
	cd backend && uv run $(PYTHON) migrate

local-makemigrations:
	@echo "📝 Gerando migrações localmente..."
	cd backend && uv run $(PYTHON) makemigrations

local-run:
	@echo "🚀 Servidor local via UV..."
	cd backend && uv run $(PYTHON) runserver

local-shell:
	@echo "🐍 Abrindo Django shell local..."
	cd backend && uv run $(PYTHON) shell

local-createsuperuser:
	@echo "👤 Criando superusuário local..."
	cd backend && uv run $(PYTHON) createsuperuser

front-dev:
	@echo "⚡ Iniciando servidor Vite local..."
	@echo "   Acesse: http://localhost:5173"
	@echo ""
	@cd frontend && npm run dev

setup-hooks:
	@echo "🪝 Configurando pre-commit hooks..."
	uv run pre-commit install
	@echo "✅ Hooks instalados! Pre-commit rodará automaticamente antes de cada commit."

# ============================================================================
# Testing & Quality
# ============================================================================
orval:
	@echo "🚀 Gerando hooks e tipos no Frontend (Orval)..."
	$(EXEC_FRONT) npm run generate:api
	@echo "✅ Frontend sincronizado com o Schema!"

openapi:
	@echo "📝 Gerando schema OpenAPI..."
	$(EXEC_BACK) uv run $(PYTHON) spectacular --file openapi.json
	@echo "✅ openapi.json atualizado!"
	@$(MAKE) orval
	@echo "✅ orval atualizado!"

test:
	@echo "🧪 Executando testes com pytest..."
	$(EXEC_BACK) uv run pytest -v

test-cov:
	@echo "🧪 Executando testes com cobertura..."
	$(EXEC_BACK) uv run pytest --cov=apps --cov-report=html --cov-report=term-missing
	@echo "📊 Relatório HTML: backend/htmlcov/index.html"

test-parallel:
	@echo "🧪 Executando testes em paralelo..."
	$(EXEC_BACK) uv run pytest -v -n auto

lint:
	$(EXEC_BACK) uv run ruff check .

lint-fix:
	$(EXEC_BACK) uv run ruff check --fix .

format:
	$(EXEC_BACK) uv run ruff format .
	$(EXEC_BACK) uv run ruff check . --fix

check: lint test openapi
	@echo "✅ Código aprovado para commit!"

fix-perms:
	@echo "🔧 Corrigindo permissões..."
	sudo chown -R $$USER:$$USER .
	@echo "✅ Permissões corrigidas!"
