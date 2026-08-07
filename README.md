# 💍 Wedding Management System

[![CI](https://github.com/Rafaelp122/wedding_management/actions/workflows/ci-pr-validation.yml/badge.svg)](https://github.com/Rafaelp122/wedding_management/actions/workflows/ci-pr-validation.yml)
[![backend](https://img.shields.io/codecov/c/github/Rafaelp122/wedding_management?flag=backend&label=backend)](https://codecov.io/gh/Rafaelp122/wedding_management)
[![frontend](https://img.shields.io/codecov/c/github/Rafaelp122/wedding_management?flag=frontend&label=frontend)](https://codecov.io/gh/Rafaelp122/wedding_management)
[![Website](https://img.shields.io/badge/website-simaceito.site-0ea5e9)](https://simaceito.site)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-3776AB)](https://python.org)
[![Django](https://img.shields.io/badge/django-5.2-092E20)](https://djangoproject.com)
[![React](https://img.shields.io/badge/react-19-61DAFB)](https://react.dev)

Sistema completo de gestão de casamentos com arquitetura moderna **React SPA + Django Ninja API**.

Este repositório centraliza o controle financeiro, logístico e de cronograma para cerimonialistas profissionais e casais, garantindo integridade de dados (Tolerância Zero) e isolamento multitenant estrito.

---

## 📖 Portal de Documentação (Princípio Diátaxis)

Nossa documentação técnica é mantida em [docs/README.md](docs/README.md) sob a metodologia **Diátaxis**. Escolha sua rota de leitura:

### 🎓 1. Tutorials (Aprendizado & Onboarding)
*Passo a passo para novos desenvolvedores:*
- **[onboarding-quickstart](docs/1-tutorials/onboarding-quickstart.md)**: Subindo o ambiente local completo (Docker, PostgreSQL, Backend, Frontend).
- **[backend-first-feature](docs/1-tutorials/backend-first-feature.md)**: Criando endpoints no Django Ninja + Service Layer.
- **[frontend-first-feature](docs/1-tutorials/frontend-first-feature.md)**: Criando telas no React + Orval + Zod.

### 🛠️ 2. How-To Guides (Receitas Práticas)
*Guias orientados a tarefas do dia a dia:*
- **[setup-local-environment](docs/2-how-to/dev-environment/setup-local-environment.md)**: Configuração de ambiente e comandos `make`.
- **[seed-database](docs/2-how-to/backend/seed-database.md)**: Populando o banco de dados local com dados fictícios (Faker) e templates.
- **[msw-testing-patterns](docs/2-how-to/frontend/msw-testing-patterns.md)**: Padrões de testes no React com MSW e RTL.

### 📋 3. Reference (Especificações Técnicas)
*Contratos de API, schemas e especificações de banco:*
- **[openapi-schema](docs/3-reference/api/openapi-schema.md)** | **[error-envelope-spec](docs/3-reference/api/error-envelope-spec.md)**
- **[commenting-standards](docs/3-reference/architecture-standards/commenting-standards.md)** | **[testing-standards](docs/3-reference/architecture-standards/testing-standards.md)**

### 💡 4. Explanation (Arquitetura & Regras de Negócio)
*Decisões de design, segurança e regras de negócio:*
- **[requirements](docs/4-explanation/requirements.md)**: Matriz de Requisitos Funcionais (RF01–RF12) e Não-Funcionais (RNF01–RNF05).
- **[system-overview](docs/4-explanation/architecture/system-overview.md)** | **[multi-tenancy-strategy](docs/4-explanation/architecture/multi-tenancy-strategy.md)**
- **[architectural-guard-rails-suite](docs/4-explanation/architecture/architectural-guard-rails-suite.md)**: Auditoria automatizada dos 12 pilares do sistema.
- **[Regras de Negócio Atômicas](docs/README.md#regras-de-negócio-atômicas)**: Integridade contábil, ciclo de vida de casamentos, máquinas de estado de contratos e proteção da agenda.

---

## 🛠 Tech Stack

- **Backend:** Python 3.12+ | Django 5.2 + Django Ninja (API-First).
- **Frontend (App):** React 19 + TypeScript + Vite + Tailwind CSS + shadcn/ui.
- **Landing Page:** Astro 6 + React + Tailwind CSS (SEO-first).
- **Banco de Dados:** PostgreSQL (Neon).
- **Infraestrutura:** Docker, Cloud Run, Vercel, Cloudflare R2 (ADR-004).

---

## 🚀 Quick Start Local

```bash
# 1. Copie e configure as variáveis de ambiente
cp .env.example .env

# 2. Inicie os containers via Docker
make up

# 3. Execute as migrations e popule os dados fictícios locais
make migrate
make seed

# 4. Inicie o servidor de desenvolvimento
make dev
```

---

## 📁 Estrutura do Monorepo

```
wedding_management/
├── backend/                  # Django Ninja API (Apps: weddings, finances, logistics, scheduler, core, tenants, users)
├── frontend/                # React SPA Principal (Feature-based structure)
├── landing/                 # Landing Page Institucional (Astro + SEO)
├── docs/                    # Documentação Técnica Oficial (Princípio Diátaxis)
├── .agents/                 # Customizações e Skills para Agentes de IA
├── .github/workflows/       # Esteiras modulares de CI, CD, E2E e Terraform
├── Makefile                 # Automação de Comandos
└── docker-compose.yml       # Orquestração de Containers
```

---

## 🧪 Qualidade, CI/CD e Integridade

- **Validação de CI Local:** `make check-ci`
- **Validação da Documentação:** `make check-docs`
- **Testes Backend (Pytest):** `make test` (ou `cd backend && uv run pytest`)
- **Testes Frontend (Vitest):** `cd frontend && pnpm run test:ci`
- **Análise Estática (Linter):** `make lint`

---

## 📝 Licença
Este projeto está licenciado sob a [MIT License](LICENSE).
