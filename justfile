set dotenv-load := true
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Exibe o menu com todos os comandos disponíveis organizados por categoria
default:
    @just --list

# Alias para exibir o menu de comandos
list:
    @just --list

# ==============================================================================
# 📦 DOCKER & AMBIENTE LOCAL
# ==============================================================================

# Executa o setup inicial do ambiente (.env, build de containers e migrations)
[group('Docker & Ambiente')]
setup: env-setup build
    @echo "✨ Setup completo! Criando superusuário..."
    just superuser

# Inicia os containers essenciais (db e backend) em segundo plano
[group('Docker & Ambiente')]
up:
    @echo "🚀 Iniciando containers essenciais (db e backend)..."
    docker compose up -d backend
    @echo "🔄 Aplicando migrações..."
    just migrate
    @echo "✅ Backend pronto em http://localhost:8000/api/v1/docs"

# Inicia os containers e acompanha os logs em tempo real
[group('Docker & Ambiente')]
dev: up
    docker compose logs -f backend db

# Reconstrói as imagens dos containers e reinicia os serviços
[group('Docker & Ambiente')]
build:
    docker compose up --build -d backend
    just migrate

# Para todos os containers em execução
[group('Docker & Ambiente')]
down:
    docker compose down

# Limpeza de imagens antigas e volumes órfãos
[group('Docker & Ambiente')]
clean:
    docker compose down -v
    docker image prune -f

# Apaga e recria o banco de dados (reseta volumes)
[group('Docker & Ambiente')]
db-reset:
    @echo "⚠️ Resetando banco de dados..."
    docker compose down -v db
    docker compose up -d backend
    just migrate
    @echo "✅ Banco de dados resetado com sucesso!"

# Segue os logs do container backend
[group('Docker & Ambiente')]
back-logs:
    docker compose logs -f backend

# Segue os logs do container frontend (se ativo no Docker)
[group('Docker & Ambiente')]
front-logs:
    docker compose logs -f frontend

# ==============================================================================
# 🐍 BACKEND & BANCO DE DADOS
# ==============================================================================

# Aplica migrações no banco de dados
[group('Backend')]
migrate:
    docker compose exec backend uv run poe migrate

# Gera novas migrações do Django
[group('Backend')]
makemigrations:
    docker compose exec backend uv run poe makemigrations

# Cria um superusuário administrativo no Django
[group('Backend')]
superuser:
    docker compose exec backend uv run poe superuser

# Abre o shell interativo do Django
[group('Backend')]
shell:
    docker compose exec backend uv run poe shell

# Popula o banco com massa de testes (Faker)
[group('Backend')]
seed-db:
    docker compose exec backend uv run poe seed-db

# Popula o banco com dados mínimos e determinísticos para testes E2E
[group('Backend')]
seed-e2e:
    docker compose exec backend uv run poe seed-e2e

# Atualiza o uv.lock do backend
[group('Backend')]
reqs:
    cd backend && uv lock

# ==============================================================================
# ⚛️ FRONTEND & LANDING PAGE
# ==============================================================================

# Inicia o servidor de desenvolvimento do Frontend (Vite)
[group('Frontend & Landing')]
frontend-dev:
    cd frontend && pnpm run dev

# Inicia o servidor de desenvolvimento da Landing Page (Astro)
[group('Frontend & Landing')]
landing-dev:
    cd landing && pnpm run dev

# Exporta o schema OpenAPI do backend e atualiza openapi.json na raiz
[group('Frontend & Landing')]
openapi:
    docker compose exec backend uv run poe openapi
    mv -f backend/openapi.json openapi.json

# Gera os hooks tipados do Orval no Frontend
[group('Frontend & Landing')]
orval:
    cd frontend && pnpm run generate:api

# Sincroniza API: gera OpenAPI + Hooks do Orval
[group('Frontend & Landing')]
sync-api: openapi orval
    @echo "🔄 Contratos de API e Frontend sincronizados com sucesso!"

# Executa testes unitários do Frontend com Vitest
[group('Frontend & Landing')]
frontend-test:
    cd frontend && pnpm test

# Executa testes do Frontend modificados no Git
[group('Frontend & Landing')]
frontend-test-changed:
    cd frontend && pnpm exec vitest run --changed

# Executa testes E2E com Playwright
[group('Frontend & Landing')]
frontend-e2e:
    docker compose exec backend uv run python manage.py flush --noinput
    docker compose exec backend uv run poe seed-e2e
    cd frontend && pnpm exec playwright test --workers=1

# Abre o relatório interativo do Playwright
[group('Frontend & Landing')]
frontend-e2e-report:
    cd frontend && pnpm exec playwright show-report

# ==============================================================================
# 🧹 QUALIDADE & CI GATES
# ==============================================================================

# Executa testes do backend com Pytest
[group('Qualidade & CI')]
test:
    docker compose exec backend uv run poe test

# Executa testes do backend com relatório de cobertura
[group('Qualidade & CI')]
test-cov:
    docker compose exec backend uv run poe test-cov

# Executa o linter Ruff no backend
[group('Qualidade & CI')]
lint:
    docker compose exec backend uv run poe lint

# Formata o código do backend com Ruff
[group('Qualidade & CI')]
format:
    docker compose exec backend uv run poe format

# Valida tipagem estática no backend com Mypy
[group('Qualidade & CI')]
mypy:
    docker compose exec backend uv run poe mypy

# Executa todos os checks de qualidade do Backend
[group('Qualidade & CI')]
check-backend:
    docker compose exec backend uv run poe check

# Executa todos os checks de qualidade do Frontend
[group('Qualidade & CI')]
check-frontend:
    cd frontend && pnpm install --frozen-lockfile && pnpm run lint && pnpm run type-check && pnpm test && pnpm run build

# Executa todos os checks de qualidade da Landing Page
[group('Qualidade & CI')]
check-landing:
    cd landing && pnpm install --frozen-lockfile && pnpm exec astro check && pnpm run build

# Executa todas as checagens e builds da documentação
[group('Qualidade & CI')]
check-docs:
    uv run --project backend python scripts/validate_docs_links.py
    uv run --project backend python scripts/validate_docs_snippets.py
    npx -y @google/design.md lint DESIGN.md
    just docs-build

# Gate completo de CI local (Docs, Backend, Frontend e Landing)
[group('Qualidade & CI')]
check-ci: check-docs check-backend check-frontend check-landing
    @echo "✅ Todos os gates de qualidade passaram com sucesso!"

# ==============================================================================
# 📚 DOCUMENTAÇÃO
# ==============================================================================

# Inicia o servidor local de documentação com live-reload (porta 8001)
[group('Documentação')]
docs-dev:
    uv run --project backend --group docs mkdocs serve -a 0.0.0.0:8001

# Compila a versão estática e estrita da documentação
[group('Documentação')]
docs-build:
    uv run --project backend --group docs mkdocs build --strict

# Publica a documentação no GitHub Pages
[group('Documentação')]
docs-gh-deploy:
    uv run --project backend --group docs mkdocs gh-deploy --force

# ==============================================================================
# 🛠️ UTILITÁRIOS
# ==============================================================================

# Cria o arquivo .env a partir do .env.example caso não exista
[group('Utilitários')]
env-setup:
    python -c "import os, shutil; shutil.copyfile('.env.example', '.env') if not os.path.exists('.env') else None"

# Gera uma nova SECRET_KEY aleatória
[group('Utilitários')]
secret-key:
    python -c "import secrets; print(secrets.token_urlsafe(50))"
