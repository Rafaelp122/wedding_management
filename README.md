# 💍 Wedding Management System - React + Django

Sistema completo de gestão de casamentos refatorado para arquitetura moderna **React SPA + Django REST API**.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)

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
│   └── requirements.txt
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

- Django 5.2 + Django REST Framework 3.16
- Autenticação JWT (Simple JWT)
- PostgreSQL / SQLite
- Celery + Redis

### Frontend

- React 18 + TypeScript + Vite
- React Router v6
- Zustand + TanStack Query
- Axios

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
# Iniciar todos os serviços
docker compose up -d

# Criar superusuário
docker compose exec backend python manage.py createsuperuser

# Ver logs
docker compose logs -f backend
```

**URLs:**

- Frontend: http://localhost:5173
- API: http://localhost:8000/api/
- Swagger Docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

### Local (sem Docker)

```bash
# Configurar ambiente Python local (recomendado para IDE)
make local-install

# Ativar ambiente virtual
source venv/bin/activate

# Backend
cd backend
python manage.py migrate
python manage.py runserver

# Frontend (outro terminal)
cd frontend && npm install && npm run dev
```

**Comando úteis:**

- `make local-install` - Cria venv e instala dependências
- `make local-clean` - Remove ambiente virtual
- `source venv/bin/activate` - Ativa o venv
- `deactivate` - Desativa o venv

---

## 📝 Licença

Projeto TCC - FIRJAN SENAI São Gonçalo
