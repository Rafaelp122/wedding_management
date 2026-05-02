# 💍 Wedding Management System

Sistema completo de gestão de casamentos com arquitetura moderna **React SPA + Django Ninja API**.

Backend organizado por **domínios de negócio** (finances, logistics, scheduler) para melhor separação de responsabilidades.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.10-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-7.2-purple.svg)](https://vitejs.dev/)

---

## 🚀 Quick Start

```bash
# 1. Configure o ambiente
cp .env.example .env  # Edite DATABASE_URL, SECRET_KEY, etc.

# 2. Inicie o sistema (Docker)
make up

# 3. Crie um superusuário
make superuser
```

**URLs:**

- Frontend: http://localhost:5173
- API: http://localhost:8000/api/v1/
- Swagger Docs: http://localhost:8000/api/v1/docs
- Admin: http://localhost:8000/admin/

---

## 📋 Documentação

- [Requisitos Funcionais e Não Funcionais](docs/REQUIREMENTS.md)
- [Guia Completo de Configuração](docs/ENVIRONMENT.md)
- [Arquitetura e Padrões de Código](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🛠 Stack Tecnológica

### Backend

- **Framework:** Django 5.2.10 + Django Ninja 1.6.2
- **Autenticação:** JWT (django-ninja-jwt 5.4.4) - Email-based login
- **Banco de Dados:** PostgreSQL 16 (produção) / SQLite (desenvolvimento)
- **Gerenciador de Pacotes:** UV (ultra-rápido, escrito em Rust)
- **Identificação:** UUID v4 (público) + BigAutoField (interno)
- **Documentação API:** Django Ninja (OpenAPI 3.0 via nativo)

### Frontend

- **Framework:** React 19.2 + TypeScript 5
- **Build Tool:** Vite 7.3.1
- **Roteamento:** React Router v7
- **Estado Global:** Zustand 5.x com persist middleware
- **Data Fetching:** TanStack Query 5.x (React Query)
- **HTTP Client:** Axios 1.13
- **Estilização:** Tailwind CSS v4.1
- **UI Components:** shadcn/ui + Lucide React icons

### DevOps

- **Containers:** Docker + Docker Compose (BuildKit habilitado)
- **Build Strategy:** Multi-stage builds (4 stages)
- **Code Quality:** Ruff 0.7.4 (linter + formatter), Pre-commit hooks
- **Testing:** Pytest 8.3 + pytest-django + factory-boy

---

## 📁 Estrutura do Projeto

```
wedding_management/
├── backend/                  # Django Ninja API
│   ├── apps/
│   │   ├── core/            # Models Base + Managers Técnicos
│   │   ├── tenants/         # Gestão de Empresas (Multi-tenancy)
│   │   ├── users/           # Usuários e Autenticação
│   │   ├── weddings/        # Wedding (núcleo do domínio)
│   │   ├── finances/        # Budget, BudgetCategory, Expense, Installment
│   │   ├── logistics/       # Supplier, Item, Contract
│   │   └── scheduler/       # Agenda e Eventos
│   ├── config/              # Settings e URLs principais
│   └── manage.py
│
├── frontend/                # React SPA
│   ├── src/
│   │   ├── components/      # Componentes UI
│   │   ├── pages/           # Telas do sistema
│   │   ├── services/        # Comunicação com API (Axios)
│   │   ├── stores/          # Estado Global (Zustand)
│   │   └── types/           # Interfaces TypeScript
│   └── package.json
│
├── docs/                    # Documentação técnica
├── .env                     # Variáveis de ambiente
├── Makefile                 # Automação de comandos
└── docker-compose.yml       # Orquestração de containers
```

---

## 🎯 Status do Projeto

✅ Autenticação JWT com email
✅ CRUD de Fornecedores
✅ Gestão de Casamentos e Orçamentos
✅ Módulo Financeiro com Parcelas
✅ Módulo de Contratos
🚧 Frontend (em desenvolvimento)
📋 Sistema de Notificações (planejado)

---

## 💻 Comandos Essenciais

### Docker (Recomendado)

```bash
make up              # Iniciar todos os serviços
make down            # Parar containers
make logs            # Ver logs de todos os containers
make migrate         # Aplicar migrações no banco
make superuser       # Criar usuário admin
make test            # Executar testes
make test-cov        # Executar testes com cobertura
make mypy            # Checagem de tipagem estática
make check-backend   # Gate de qualidade do backend
make check-frontend  # Gate de qualidade do frontend
make check-ci        # Gate local espelhando CI
make shell           # Django shell
```

### Desenvolvimento Local (sem Docker)

```bash
# Backend
cd backend && uv sync --group dev
cd backend && uv run python manage.py runserver

# Frontend
cd frontend && npm ci && npm run dev
```

> 📖 **Lista completa de comandos:** [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)

---

## 🧪 Qualidade de Código

O projeto usa **pre-commit hooks** obrigatórios (instalados automaticamente):

- ✅ Ruff linter + formatter
- ✅ Trailing whitespace check
- ✅ YAML validator

```bash
make lint            # Verificar problemas
make format          # Formatar código
make mypy            # Verificar tipagem
make test            # Executar testes
make test-cov        # Testes com cobertura
```

---

## 📝 Licença

Projeto Integrador - FIRJAN SENAI São Gonçalo
