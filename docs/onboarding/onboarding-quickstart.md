# Tutorial: Onboarding & Quickstart do Ambiente de Desenvolvimento

> **Objetivo:** Subir o ambiente local completo (Docker, PostgreSQL, Django Backend, React Frontend SPA e Landing Page em Astro) do zero.
> **Público:** Novos desenvolvedores onboarding no projeto.
> **Relacionados:** [Workflow GitOps](gitops-sprint-workflow.md) · [Primeira Feature Backend](backend-first-feature.md) · [Primeira Feature Frontend](frontend-first-feature.md) · [Landing Page Spec](../reference/frontend/landing-page-spec.md)

---

## Pré-requisitos

Certifique-se de ter instalado em sua máquina local:
- **Python 3.12+** e [`uv`](https://docs.astral.sh/uv/) (gerenciador de dependências e ambientes virtuais Python)
- **Node.js 22+** e [`pnpm`](https://pnpm.io/) (versão 9.15+)
- **Docker & Docker Compose**
- **Git**

---

## Método 1: Setup Expresso via Makefile (Recomendado)

O repositório possui um `Makefile` automatizado que configura todo o ambiente em poucos comandos:

```bash
# 1. Clonar repositório e preparar arquivos .env
git clone git@github.com:Rafaelp122/wedding_management.git
cd wedding_management
make env-setup

# 2. Inicializar banco de dados e backend no Docker com migrações
make up

# 3. Criar superusuário administrativo
make superuser

# 4. Iniciar servidores de desenvolvimento (no Host)
make frontend-dev   # Terminal 1: SPA React 19 na porta 5173
make landing-dev    # Terminal 2: Landing Page Astro na porta 4321
```

---

## Método 2: Setup Manual por Aplicação

Se você preferir executar cada serviço individualmente no host local com `uv` e `pnpm`:

### Passo 1: Configurar Variáveis de Ambiente

```bash
# Backend .env
cp backend/.env.example backend/.env

# Frontend .env
cp frontend/.env.example frontend/.env
```

### Passo 2: Subir o Banco de Dados (PostgreSQL Docker)

```bash
docker compose up -d db
```

### Passo 3: Inicializar o Backend Python (Django Ninja)

```bash
cd backend
uv sync --all-groups
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver 0.0.0.0:8000
```
O backend estará acessível em [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs) (OpenAPI Swagger UI).

### Passo 4: Inicializar o Frontend SPA (React 19 + Vite)

Em outro terminal:
```bash
cd frontend
pnpm install
pnpm run dev
```
O frontend SPA estará acessível em [`http://localhost:5173`](http://localhost:5173).

### Passo 5: Inicializar a Landing Page Comercial (Astro 7)

Em outro terminal:
```bash
cd landing
pnpm install
pnpm run dev
```
A Landing Page estará acessível em [`http://localhost:4321`](http://localhost:4321).

---

## Painel de Serviços e Portas Locais

| Serviço | URL Local | Descrição |
| :--- | :--- | :--- |
| **Landing Page Comercial** | [`http://localhost:4321`](http://localhost:4321) | Portal público e comercial em Astro 7 com React Islands |
| **Frontend SPA** | [`http://localhost:5173`](http://localhost:5173) | Interface autenticada em React 19 + Vite |
| **Backend REST API** | [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs) | Swagger UI interativo do Django Ninja |
| **Portal MkDocs** | [`http://localhost:8001`](http://localhost:8001) | Documentação técnica local (`make docs-dev`) |
