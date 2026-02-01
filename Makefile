SHELL := /bin/bash
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help up down build rebuild clean logs restart
.PHONY: migrate makemigrations db-reset superuser shell back-shell back-logs reqs back-install
.PHONY: front-install front-shell front-logs
.PHONY: test test-cov test-parallel lint lint-fix format clean-cache fix-perms
.PHONY: secret-key env-setup local-install local-clean

# Default target
help:
	@echo "=========================================================================="
	@echo "  💍 Wedding Management - Sistema de Gestão de Casamentos"
	@echo "=========================================================================="
	@echo ""
	@echo "📦 DOCKER & ORQUESTRAÇÃO"
	@echo "  make up                  - Inicia containers, migrations e exibe logs"
	@echo "  make down                - Para e remove todos os containers"
	@echo "  make build               - Reconstrói e inicia os containers"
	@echo "  make rebuild             - Reconstrói do zero (sem cache)"
	@echo "  make clean               - Limpeza total (containers, volumes, redes)"
	@echo "  make logs                - Exibe logs de todos os containers"
	@echo "  make restart             - Reinicia containers"
	@echo ""
	@echo "🐍 BACKEND (Django REST Framework)"
	@echo "  make migrate             - Aplica migrações no banco de dados"
	@echo "  make makemigrations      - Gera novos arquivos de migração"
	@echo "  make db-reset            - ⚠️  APAGA banco e migrations, recria tudo"
	@echo "  make superuser           - Cria usuário administrativo"
	@echo "  make shell               - Acessa shell interativo do Django"
	@echo "  make back-install        - Instala pacote Python (pkg=nome)"
	@echo "  make reqs                - Atualiza requirements.txt"
	@echo "  make back-shell          - Acessa terminal do container backend"
	@echo "  make back-logs           - Exibe logs do backend"
	@echo ""
	@echo "🔐 CONFIGURAÇÃO & AMBIENTE"
	@echo "  make secret-key          - Gera SECRET_KEY segura para Django"
	@echo "  make env-setup           - Configura arquivo .env (copia .env.example)"
	@echo "  make local-install       - Instala deps localmente (venv + requirements.txt)"
	@echo "  make local-clean         - Remove ambiente virtual local"
	@echo ""
	@echo "⚛️  FRONTEND (React + Vite)"
	@echo "  make front-install       - Instala deps npm (pkg=nome para específico)"
	@echo "  make front-shell         - Acessa terminal do container frontend"
	@echo "  make front-logs          - Exibe logs do frontend"
	@echo ""
	@echo "🧹 QUALIDADE & MANUTENÇÃO"
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

up:
	@echo "🚀 Iniciando containers..."
	docker compose up -d
	@echo "🔄 Aplicando migrations..."
	@sleep 3
	docker compose exec backend python manage.py migrate
	@echo "✅ Containers prontos!"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Admin:    http://localhost:8000/admin"
	@echo ""
	@echo "📋 Exibindo logs (Ctrl+C para sair)..."
	docker compose logs -f

build:
	@echo "🔨 Reconstruindo e iniciando containers..."
	docker compose up --build -d
	@echo "🔄 Aplicando migrations..."
	@sleep 3
	docker compose exec backend python manage.py migrate
	@echo "✅ Containers prontos!"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Admin:    http://localhost:8000/admin"
	@echo ""
	@echo "📋 Exibindo logs (Ctrl+C para sair)..."
	docker compose logs -f

rebuild:
	@echo "🔨 Reconstruindo do zero (sem cache)..."
	docker compose build --no-cache
	docker compose up -d
	@echo "🔄 Aplicando migrations..."
	@sleep 3
	docker compose exec backend python manage.py migrate
	@echo "✅ Containers prontos!"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Backend:  http://localhost:8000"
	@echo "   Admin:    http://localhost:8000/admin"
	@echo ""
	@echo "📋 Exibindo logs (Ctrl+C para sair)..."
	docker compose logs -f

down:
	@echo "🛑 Parando containers..."
	docker compose down

clean:
	@echo "🧹 Limpeza total (containers, volumes, redes)..."
	docker compose down -v
	docker system prune -f
	@echo "✅ Limpeza concluída!"

logs:
	docker compose logs -f

restart:
	@echo "🔄 Reiniciando containers..."
	docker compose restart

# ============================================================================
# Backend Commands
# ============================================================================

migrate:
	@echo "🔄 Aplicando migrations..."
	docker compose exec backend python manage.py migrate

makemigrations:
	@echo "📝 Criando migrations..."
	docker compose exec backend python manage.py makemigrations

db-reset:
	@echo "⚠️  ATENÇÃO: Este comando vai APAGAR o banco de dados e todas as migrations!"
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
	echo "🗑️  Parando containers..."; \
	docker compose down -v; \
	echo "🗑️  Removendo arquivos de migration..."; \
	find backend/apps -path "*/migrations/*.py" -not -name "__init__.py" -delete; \
	find backend/apps -path "*/migrations/__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true; \
	echo "🚀 Recriando containers..."; \
	docker compose up -d; \
	sleep 5; \
	echo "📝 Gerando novas migrations..."; \
	for app in users weddings scheduler items contracts; do \
	docker compose exec backend python manage.py makemigrations $$app; \
	done; \
	echo "✅ Aplicando migrations..."; \
	docker compose exec backend python manage.py migrate; \
	echo "🎉 Reset completo! Agora crie um superuser com 'make superuser'"; \
	else \
	echo "❌ Operação cancelada."; \
	fi

superuser:
	docker compose exec backend python manage.py createsuperuser

shell:
	docker compose exec backend python manage.py shell

back-shell:
	docker compose exec backend /bin/sh

back-logs:
	docker compose logs -f backend

reqs:
	docker compose exec backend pip freeze > backend/requirements.txt
	@echo "✅ requirements.txt atualizado!"

back-install:
	docker compose exec backend pip install $(pkg)
	$(MAKE) reqs

# ============================================================================
# Frontend Commands
# ============================================================================

front-install:
	docker compose exec frontend npm install $(pkg)

front-shell:
	docker compose exec frontend sh

front-logs:
	docker compose logs -f frontend

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

local-install:
	@echo "🐍 Configurando ambiente Python local..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "📦 Criando ambiente virtual..."; \
		python3 -m venv $(VENV); \
	fi
	@echo "📥 Instalando dependências do backend..."
	@$(PIP) install --upgrade pip > /dev/null 2>&1
	@$(PIP) install -r backend/requirements.txt
	@echo ""
	@echo "✅ Ambiente local configurado com sucesso!"
	@echo ""
	@echo "Para ativar o ambiente virtual:"
	@echo "  source $(VENV)/bin/activate"
	@echo ""
	@echo "Para desativar:"
	@echo "  deactivate"

local-clean:
	@echo "🗑️  Removendo ambiente virtual local..."
	@rm -rf $(VENV)
	@echo "✅ Ambiente virtual removido!"

# ============================================================================
# Testing & Quality
# ============================================================================

test:
	@echo "🧪 Executando testes com pytest..."
	docker compose exec backend pytest -v || echo "⚠️  Nenhum teste encontrado ou testes falharam"

test-cov:
	@echo "🧪 Executando testes com cobertura..."
	docker compose exec backend pytest --cov=apps --cov-report=html --cov-report=term-missing
	@echo "📊 Relatório HTML: backend/htmlcov/index.html"

test-parallel:
	@echo "🧪 Executando testes em paralelo..."
	docker compose exec backend pytest -v -n auto

lint:
	@echo "🔍 Executando linter..."
	docker compose exec backend ruff check .

lint-fix:
	@echo "🔧 Corrigindo problemas de lint..."
	docker compose exec backend ruff check --fix .

format:
	@echo "✨ Formatando código..."
	docker compose exec backend ruff format .
	docker compose exec backend ruff check . --fix

fix-perms:
	@echo "🔧 Corrigindo permissões..."
	sudo chown -R $$USER:$$USER .
	@echo "✅ Permissões corrigidas!"
