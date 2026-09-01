# Wedding Management System

<p align="center">
  <strong>Plataforma SaaS Multi-Tenant de Alta Confiabilidade para Gestão de Casamentos, Orçamentos e Fornecedores.</strong>
</p>

<p align="center">
  <a href="https://rafaelp122.github.io/wedding_management/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-7C3AED?logo=materialformkdocs&logoColor=white&style=flat-square" alt="Documentation"></a>
  <a href="https://github.com/Rafaelp122/wedding_management/actions/workflows/ci-pr-validation.yml"><img src="https://img.shields.io/github/actions/workflow/status/Rafaelp122/wedding_management/ci-pr-validation.yml?branch=main&label=CI&style=flat-square" alt="CI"></a>
  <a href="https://github.com/Rafaelp122/wedding_management/actions/workflows/docs-ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Rafaelp122/wedding_management/docs-ci.yml?branch=main&label=Docs%20CI&style=flat-square" alt="Docs CI"></a>
  <a href="https://codecov.io/gh/Rafaelp122/wedding_management"><img src="https://img.shields.io/codecov/c/github/Rafaelp122/wedding_management?flag=backend&label=backend&style=flat-square" alt="Backend Coverage"></a>
  <a href="https://simaceito.site"><img src="https://img.shields.io/badge/website-simaceito.site-0ea5e9?style=flat-square" alt="Website"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white&style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/django-6.0-092E20?logo=django&logoColor=white&style=flat-square" alt="Django">
  <img src="https://img.shields.io/badge/django--ninja-1.6+-087EA4?style=flat-square" alt="Django Ninja">
  <img src="https://img.shields.io/badge/react-19-61DAFB?logo=react&logoColor=black&style=flat-square" alt="React 19">
  <img src="https://img.shields.io/badge/astro-7.1-FF5D01?logo=astro&logoColor=white&style=flat-square" alt="Astro 7">
  <img src="https://img.shields.io/badge/tailwind-v4-38B2AC?logo=tailwindcss&logoColor=white&style=flat-square" alt="Tailwind CSS v4">
  <img src="https://img.shields.io/badge/postgresql-neon-00E599?logo=postgresql&logoColor=black&style=flat-square" alt="Neon DB">
  <img src="https://img.shields.io/badge/storage-cloudflare--r2-F38020?logo=cloudflare&logoColor=white&style=flat-square" alt="Cloudflare R2">
  <img src="https://img.shields.io/badge/iac-terraform-7B42BC?logo=terraform&logoColor=white&style=flat-square" alt="Terraform">
  <img src="https://img.shields.io/badge/e2e-playwright-2EAD33?logo=playwright&logoColor=white&style=flat-square" alt="Playwright">
</p>

---

## 📖 Portal Oficial de Documentação Técnica

A documentação técnica oficial da plataforma está disponível online via GitHub Pages:

👉 **[https://rafaelp122.github.io/wedding_management/](https://rafaelp122.github.io/wedding_management/)**

Construída sob a metodologia **Diátaxis** e o modelo de **Notas Atômicas (Zettelkasten)**, a documentação é 100% sincronizada com o código-fonte da aplicação através de transclusão de snippets (`--8<--`) auditados continuamente em CI/CD:

| Seção do Portal | URL / Destino | O que você encontra |
| :--- | :--- | :--- |
| **1. Início** | [`/`](https://rafaelp122.github.io/wedding_management/) | Visão executiva, pilares de engenharia, quickstart e diagrama fullstack. |
| **2. Funcionalidades** | [`/features/`](https://rafaelp122.github.io/wedding_management/features/) | Showcase de produto: Módulo Financeiro, Gestão de Contratos e Agenda com templates. |
| **3. Arquitetura** | [`/architecture/`](https://rafaelp122.github.io/wedding_management/architecture/) | System Design fullstack, os 10 Bounded Contexts (ERDs), Regras de Negócio e Catálogo de ADRs (001–028). |
| **4. Guias & Onboarding** | [`/guides/`](https://rafaelp122.github.io/wedding_management/guides/) | Trilhas passo a passo para novos engenheiros, receitas de backend/frontend e playbooks de troubleshooting. |
| **5. Referência Técnica** | [`/reference/`](https://rafaelp122.github.io/wedding_management/reference/) | Contratos OpenAPI 3.1, Modelos Core (`BaseModel`/`TenantModel`), Módulos Terraform, Suíte de Testes e Guard-Rails. |

---

## 🏛️ Pilares de Engenharia & Arquitetura

- **Tolerância Zero Financeira ([ADR-010](https://rafaelp122.github.io/wedding_management/architecture/adr/010-tolerance-zero/)):** Conservação exata de centavos em rateios de despesas (`DecimalField(12, 2)`) com absorção de resíduos na última parcela e proteção contra desvios contábeis.
- **Isolamento Multi-Tenant Pragmático ([ADR-009](https://rafaelp122.github.io/wedding_management/architecture/adr/009-multitenancy/), [ADR-016](https://rafaelp122.github.io/wedding_management/architecture/adr/016-pragmatic-multi-tenancy/)):** Isolamento lógico por coluna (`company_id`), encapsulado em `TenantQuerySet` e validado obrigatoriamente no Service Layer.
- **Service Layer Pattern & CQRS ([ADR-006](https://rafaelp122.github.io/wedding_management/architecture/adr/006-service-layer/)):** Rotas do Django Ninja delegam mutações a `services/` (envolvidos em `@transaction.atomic` e `full_clean()`) e consultas a `selectors/`.
- **Contratos Tipados de Ponta a Ponta ([ADR-012](https://rafaelp122.github.io/wedding_management/architecture/adr/012-orval-contract-driven-frontend/)):** Django Ninja -> OpenAPI 3.1 -> Orval -> TanStack Query + Zod no React 19, eliminando clientes HTTP manuais.
- **Upload Direto no Cloudflare R2 ([ADR-003](https://rafaelp122.github.io/wedding_management/architecture/adr/003-why-r2/), [ADR-004](https://rafaelp122.github.io/wedding_management/architecture/adr/004-presigned-urls/)):** Upload de PDFs contratuais direto do browser via Presigned URLs com custo zero de egresso.
- **Barreira Dinâmica de Guard-Rails:** Testes arquiteturais com análise de AST Python que bloqueiam chamadas ORM desprotegidas e mutações sem transações atômicas.

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Detalhes & Responsabilidades |
| :--- | :--- | :--- |
| **Backend REST API** | Python 3.12+ · Django 6.0 · Django Ninja 1.6+ | API-First fortemente tipada com Pydantic v2, autenticação JWT e documentação Swagger nativa. |
| **Frontend SPA** | React 19.2 · TypeScript 7 · Vite 8.2 · Tailwind CSS v4 | Interface rica e autenticada com shadcn/ui, TanStack Query e formulários React Hook Form + Zod. |
| **Landing Page Comercial**| Astro 7.1 · React 19 Islands · Tailwind CSS v4 | Portal institucional público de alta conversão com Static Site Generation (SSG) e SEO otimizado. |
| **Persistência de Dados** | Neon Serverless PostgreSQL (`psycopg 3`) | Banco relacional escalável com isolamento lógico multi-tenant. |
| **Armazenamento de PDFs** | Cloudflare R2 (S3-Compatible API) | Armazenamento de arquivos anexos com transferência direta e custo zero de egress. |
| **Tarefas & Workers** | Huey · Redis/Valkey · GCP Cloud Scheduler | Filas assíncronas em segundo plano e cron tasks automatizadas via OIDC. |
| **Infraestrutura & IaC** | Terraform 1.10+ · GCP Cloud Run · GitHub Actions | Infraestrutura como código declarativa e esteiras automatizadas de GitOps. |
| **Qualidade & Testes** | Pytest · Vitest · Playwright E2E · Ruff · Mypy | Pirâmide completa de testes unitários, integração e automação ponta a ponta. |

---

## 🚀 Quickstart Local (Ambiente em 2 Minutos)

### Instalação Rápida do Just (Runner Universal)

O projeto utiliza o **[just](https://github.com/casey/just)** como executor de tarefas moderno e multiplataforma:

- **Windows**: `winget install Casey.Just` ou `scoop install just` ou `choco install just`
- **macOS**: `brew install just`
- **Linux (Ubuntu/Debian)**: `sudo apt install just` (ou `cargo install just` / `pacman -S just`)

---

### Método 1: Via Just (Recomendado)

```bash
# 1. Clonar repositório e preparar ambiente
git clone git@github.com:Rafaelp122/wedding_management.git
cd wedding_management

# 2. Inicializar variáveis de ambiente, containers e banco de dados
just setup        # Executa env-setup, sobe os containers e cria o superusuário

# 3. Iniciar servidores de desenvolvimento no Host
just frontend-dev   # Terminal 1: SPA React 19 na porta 5173
just landing-dev    # Terminal 2: Landing Page Astro na porta 4321
just docs-dev       # Terminal 3: Documentação MkDocs na porta 8001
```

---

### Método 2: Nativo Direto (Docker Compose, uv & pnpm)

Caso prefira executar as etapas diretamente no terminal sem o `just`:

```bash
# 1. Preparar variáveis de ambiente
cp .env.example .env

# 2. Inicializar banco de dados e backend no Docker (com migrações)
docker compose up -d backend
docker compose exec backend uv run poe migrate
docker compose exec backend uv run poe superuser

# 3. Iniciar servidores de desenvolvimento no Host
cd frontend && pnpm dev                # Terminal 1: SPA React 19 na porta 5173
cd landing && pnpm dev                 # Terminal 2: Landing Page Astro na porta 4321
uv run --project backend --group docs mkdocs serve -a 0.0.0.0:8001 # Terminal 3: MkDocs na porta 8001
```

### Painel de Serviços Locais

| Serviço | URL Local | Comando (`just`) | Comando Nativo |
| :--- | :--- | :--- | :--- |
| **Landing Page Comercial** | [`http://localhost:4321`](http://localhost:4321) | `just landing-dev` | `cd landing && pnpm dev` |
| **Frontend SPA (App)** | [`http://localhost:5173`](http://localhost:5173) | `just frontend-dev` | `cd frontend && pnpm dev` |
| **Backend Swagger OpenAPI**| [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs) | `just up` / `just dev` | `docker compose up -d backend` |
| **Documentação MkDocs** | [`http://localhost:8001`](http://localhost:8001) | `just docs-dev` | `uv run --project backend --group docs mkdocs serve` |

---

## 📂 Estrutura do Monorepo

```text
wedding_management/
├── backend/                  # Django 6.0 + Django Ninja REST API
│   ├── apps/                 # 10 Bounded Contexts (core, tenants, users, weddings, finances, logistics, scheduler...)
│   └── config/               # Settings por ambiente (development, test, production)
├── frontend/                 # React 19 SPA (Feature-based structure com Orval e Tailwind v4)
├── landing/                  # Landing Page Comercial (Astro 7 + React Islands)
├── docs/                     # Portal de Documentação Oficial (Diátaxis & Notas Atômicas)
├── scripts/                  # Scripts de validação de links, snippets e auditoria
├── .agents/                  # Skills operacionais para agentes e subagentes
├── .github/workflows/        # Workflows modulares de CI, CD, Docs e Terraform
├── justfile                  # Orquestração de comandos moderna e multiplataforma
└── docker-compose.yml        # Orquestração de containers locais
```

---

## 🧪 Comandos Essenciais de Qualidade & CI

```bash
# Executa todos os testes e gates de CI locais (Docs, Backend, Frontend e Landing)
just check-ci

# Validação e build estrito da documentação
just check-docs

# Testes unitários e de integração do backend (Pytest)
just test

# Testes do frontend (Vitest)
just frontend-test

# Testes ponta a ponta (Playwright E2E)
just frontend-e2e

# Sincronização de contratos (OpenAPI -> Orval -> TypeScript)
just sync-api
```

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
