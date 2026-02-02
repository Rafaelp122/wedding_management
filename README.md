# 💍 Wedding Management System - React + Django

Sistema completo de gestão de casamentos refatorado para arquitetura moderna **React SPA + Django REST API**.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.10-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3-purple.svg)](https://vitejs.dev/)

---

## 📁 Estrutura do Projeto

```
wedding_management/
├── backend/                  # Django REST API
│   ├── apps/
│   │   ├── suppliers/       # Gestão de Fornecedores
│   │   ├── weddings/        # Core (Casamento + Orçamento)
│   │   ├── items/           # Itens Logísticos + Financeiro
│   │   ├── contracts/       # Gestão de Contratos
│   │   └── scheduler/       # Agenda e Eventos
│   ├── config/              # Settings e URLs principais
│   ├── manage.py
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/                # React SPA
│   ├── src/
│   │   ├── components/      # Componentes UI
│   │   ├── hooks/           # Custom Hooks
│   │   ├── pages/           # Telas do sistema
│   │   ├── services/        # Comunicação com API (Axios)
│   │   ├── stores/          # Estado Global (Zustand)
│   │   ├── types/           # Interfaces TypeScript
│   │   └── utils/           # Funções auxiliares
│   └── package.json
│
├── docs/                    # Documentação do projeto
├── .env                     # Variáveis de ambiente unificadas
├── Makefile                 # Automação de comandos
└── docker-compose.yml       # Orquestração de containers
```

---

## 🛠 Stack Tecnológica

### Backend

- **Framework:** Django 5.2.10 + Django REST Framework 3.16.1
- **Autenticação:** JWT (djangorestframework-simplejwt 5.4) - Email-based login
- **Banco de Dados:** PostgreSQL 16 (produção) / SQLite (desenvolvimento)
- **Gerenciador de Pacotes:** UV (ultra-rápido, escrito em Rust)
- **Dependências:** pyproject.toml + uv.lock (PEP 621)
- **Identificação:** UUID7 (ordenado por tempo) para todas as entidades
- **Documentação API:** drf-spectacular (OpenAPI 3.0)

### Frontend

- **Framework:** React 19.2 + TypeScript 5
- **Build Tool:** Vite 7.3.1
- **Roteamento:** React Router v7
- **Estado Global:** Zustand 5.x com persist middleware
- **Data Fetching:** TanStack Query 5.x (React Query)
- **HTTP Client:** Axios 1.13
- **Estilização:** Tailwind CSS v4.1 com @tailwindcss/postcss
- **UI Components:** shadcn/ui + Lucide React icons

### DevOps & Ferramentas

- **Containers:** Docker + Docker Compose com BuildKit habilitado
- **Build Strategy:** Multi-stage builds (4 stages: base, builder, development, production)
- **Code Quality:** Ruff 0.7.4 (linter + formatter), Pre-commit hooks
- **Testing:** Pytest 8.3 + pytest-django + factory-boy

---

## ⚙️ Configuração de Ambiente

> 📖 **Documentação completa:** [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)

### Quick Start

```bash
# 1. Configurar .env
make env-setup

# 2. Gerar SECRET_KEY segura
make secret-key

# 3. Copiar a chave gerada e colar no .env
nano .env
```

**Principais variáveis:**

- `SECRET_KEY` - Chave criptográfica (gerar com `make secret-key`)
- `DEBUG` - Modo debug (`True`/`False`)
- `DB_*` - Configurações do PostgreSQL
- `ACCESS_TOKEN_LIFETIME_MINUTES` - Duração do JWT (padrão: 15 min)

---

## 🚀 Desenvolvimento

### Docker (Recomendado)

```bash
# Iniciar todos os serviços (containers + migrations + logs)
make up

# Apenas buildar e iniciar (sem logs)
make build

# Rebuild completo (sem cache - use apenas se necessário)
make rebuild

# Criar superusuário
make superuser

# Ver logs de todos os containers
make logs

# Ver logs apenas do backend
make back-logs

# Ver logs apenas do frontend
make front-logs

# Parar containers
make down

# Limpar tudo (containers + volumes + imagens)
make clean
```

**URLs:**

- Frontend: http://localhost:5173
- API: http://localhost:8000/api/
- Swagger Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

### Desenvolvimento Local (sem Docker)

**Pré-requisitos:**

- Python 3.11+ instalado
- Node.js 22+ (para frontend)
- UV (instalado automaticamente por `make local-install`)

**Setup inicial:**

```bash
# 1. Configurar ambiente Python local (cria venv e instala dependências)
# Este comando também instala UV (se necessário) e configura pre-commit hooks
make local-install

# Se UV foi instalado agora, recarregue o shell e rode novamente:
source ~/.cargo/env
make local-install

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Aplicar migrações
make local-migrate

# 4. Criar superusuário
make local-createsuperuser

# 5. Iniciar backend (terminal 1)
make local-run

# 6. Instalar dependências do frontend
cd frontend && npm install

# 7. Iniciar frontend (terminal 2)
make front-dev
```

**Comandos locais disponíveis:**

- `make local-run` - Inicia servidor Django (http://localhost:8000)
- `make local-migrate` - Aplica migrações no banco
- `make local-makemigrations` - Gera novos arquivos de migração
- `make local-shell` - Abre Django shell
- `make local-createsuperuser` - Cria usuário admin
- `make front-dev` - Inicia servidor Vite (http://localhost:5173)
- `make setup-hooks` - Reinstala pre-commit hooks (se necessário)
- `deactivate` - Desativa o ambiente virtual

**Pre-commit Hooks:**

O projeto usa pre-commit hooks obrigatórios para garantir qualidade de código. Eles são instalados automaticamente por `make local-install` e executam:

- ✅ Ruff linter + formatter (corrige problemas automaticamente)
- ✅ Trailing whitespace check
- ✅ End of file fixer
- ✅ YAML validator
- ✅ Large files check

**Se um commit for bloqueado pelos hooks**, corrija os problemas e commite novamente. Na maioria dos casos, Ruff corrige automaticamente.

### Comandos Úteis

**Gerenciamento de Dependências:**

```bash
# Backend - Instalar pacote Python
make back-install pkg=nome-do-pacote

# Backend - Atualizar uv.lock após mudanças no pyproject.toml
make reqs

# Frontend - Instalar pacote npm
make front-install pkg=nome-do-pacote
```

**Banco de Dados:**

```bash
# Criar migrações
make makemigrations

# Aplicar migrações
make migrate

# Resetar banco (APAGA TUDO)
make db-reset

# Django shell
make shell
```

**Qualidade de Código:**

```bash
# Lint (verifica problemas)
make lint

# Lint + Fix (corrige automaticamente)
make lint-fix

# Formatar código
make format

# Testes
make test

# Testes com cobertura
make test-cov

# Testes em paralelo
make test-parallel
```

**Acesso a Shells:**

```bash
# Shell do container backend (bash)
make back-shell

# Shell do container frontend (sh)
make front-shell

# Django shell (Python)
make shell
```

### Hot Reload

⚡ **Desenvolvimento com hot reload habilitado:**

- **Backend:** Django autoreload detecta mudanças em arquivos `.py`
- **Frontend:** Vite HMR (Hot Module Replacement) atualiza instantaneamente
- **Não precisa rebuild** para mudanças em código
- **Precisa rebuild** apenas ao adicionar/remover pacotes no pyproject.toml ou package.json

---

## 📝 Licença

Projeto TCC - FIRJAN SENAI São Gonçalo
