# Tutorial: Onboarding & Quickstart do Ambiente de Desenvolvimento

> **Objetivo:** Subir o ambiente local completo (Docker, PostgreSQL, Django Backend, React Frontend SPA e Landing Page em Astro) do zero.
> **Público:** Novos desenvolvedores onboarding no projeto.
> **Relacionados:** [Workflow GitOps](gitops-sprint-workflow.md) · [Primeira Feature Backend](backend-first-feature.md) · [Primeira Feature Frontend](frontend-first-feature.md) · [Setup Local Completo](../guides/dev-environment/setup-local-environment.md) · [Task Runner Just](../guides/dev-environment/task-runner-just.md) · [Landing Page Spec](../reference/frontend/landing-page-spec.md)

---

## Pré-requisitos

Certifique-se de ter instalado em sua máquina local:
- **Python 3.12+** e [`uv`](https://docs.astral.sh/uv/) (gerenciador de dependências e ambientes virtuais Python)
- **Node.js 22+** e [`pnpm`](https://pnpm.io/) (versão 9.15+)
- **Docker & Docker Compose**
- **Git**
- **`just`** (Opcional / Recomendado — [Guia do Task Runner Just](../guides/dev-environment/task-runner-just.md))

---

## Trilha 1: Trilha Rápida com `just` (Recomendada)

O repositório disponibiliza um `justfile` orquestrador que automatiza todo o ciclo de vida do ambiente:

```bash
# 1. Clonar repositório e executar setup completo (.env, containers e migrações)
git clone git@github.com:Rafaelp122/wedding_management.git
cd wedding_management
just setup

# 2. Iniciar servidores de desenvolvimento (no Host)
just frontend-dev   # Terminal 1: SPA React 19 na porta 5173
just landing-dev    # Terminal 2: Landing Page Astro na porta 4321
```

> [!TIP]
> Caso prefira executar o passo a passo com `just`:
> ```bash
> just env-setup   # Cria o .env local a partir do template
> just up          # Sobe db + backend e aplica migrações
> just superuser   # Cria o superusuário administrativo
> ```

---

## Trilha 2: Trilha Nativa Direta (Docker, `uv` e `pnpm`)

Caso prefira não utilizar o `just` ou precise rodar comandos diretamente em ambientes isolados:

### Passo 1: Configurar Variáveis de Ambiente

```bash
# Cria o arquivo .env a partir do template .env.example
python -c "import os, shutil; shutil.copyfile('.env.example', '.env') if not os.path.exists('.env') else None"
```

### Passo 2: Inicializar o Banco de Dados e Backend no Docker

```bash
# Sobe os containers essenciais (db e backend)
docker compose up -d backend

# Aplica as migrações no banco de dados
docker compose exec backend uv run poe migrate

# Cria o superusuário administrativo interativo
docker compose exec backend uv run poe superuser
```

O backend estará acessível em [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs) (OpenAPI Swagger UI).

> [!NOTE]
> Se preferir rodar o Backend diretamente no Host (sem container Docker para o backend):
> ```bash
> docker compose up -d db
> cd backend
> uv sync --all-groups
> uv run poe migrate
> uv run poe superuser
> uv run python manage.py runserver 0.0.0.0:8000
> ```

### Passo 3: Inicializar o Frontend SPA (React 19 + Vite)

Em outro terminal:
```bash
cd frontend
pnpm install
pnpm run dev
```
O frontend SPA estará acessível em [`http://localhost:5173`](http://localhost:5173).

### Passo 4: Inicializar a Landing Page Comercial (Astro 7)

Em outro terminal:
```bash
cd landing
pnpm install
pnpm run dev
```
A Landing Page estará acessível em [`http://localhost:4321`](http://localhost:4321).

---

## Comandos Essenciais de Validação e Testes

| Ação | Trilha com `just` | Trilha Nativa Direta |
| :--- | :--- | :--- |
| **Testes do Backend** | `just test` | `docker compose exec backend uv run poe test` |
| **Testes com Cobertura** | `just test-cov` | `docker compose exec backend uv run poe test-cov` |
| **Testes do Frontend** | `just frontend-test` | `cd frontend && pnpm test` |
| **Testes E2E (Playwright)** | `just frontend-e2e` | `docker compose exec backend uv run python manage.py flush --noinput && docker compose exec backend uv run poe seed-e2e && cd frontend && pnpm exec playwright test --workers=1` |
| **Sincronizar API (Orval)** | `just sync-api` | `docker compose exec backend uv run poe openapi && mv backend/openapi.json openapi.json && cd frontend && pnpm run generate:api` |
| **Validação de Docs & Links**| `just check-docs` | `uv run --project backend python scripts/validate_docs_links.py && uv run --project backend python scripts/validate_docs_snippets.py && npx -y @google/design.md lint DESIGN.md && uv run --project backend --group docs mkdocs build --strict` |
| **Quality Gate Completo (CI)**| `just check-ci` | Execução sequencial de docs, backend, frontend e landing |

---

## Painel de Serviços e Portas Locais

| Serviço | URL Local | Trilha `just` | Trilha Nativa Direta | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **Landing Page Comercial** | [`http://localhost:4321`](http://localhost:4321) | `just landing-dev` | `cd landing && pnpm run dev` | Portal público em Astro 7 com React Islands |
| **Frontend SPA** | [`http://localhost:5173`](http://localhost:5173) | `just frontend-dev` | `cd frontend && pnpm run dev` | Interface autenticada em React 19 + Vite |
| **Backend REST API** | [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs) | `just up` / `just dev` | `docker compose up -d backend` | Swagger UI interativo do Django Ninja |
| **Portal MkDocs** | [`http://localhost:8001`](http://localhost:8001) | `just docs-dev` | `uv run --project backend --group docs mkdocs serve -a 0.0.0.0:8001` | Documentação técnica local com live-reload |
| **PostgreSQL Database** | `localhost:5432` | `just up` | `docker compose up -d db` | Banco de dados relacional (PostgreSQL 17) |
