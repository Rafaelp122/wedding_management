# Tutorial: Onboarding & Quickstart do Ambiente de Desenvolvimento

> **Objetivo:** Subir o ambiente local completo (Docker, PostgreSQL, Django Backend e React Frontend) do zero.
> **Público:** Novos desenvolvedores onboarding no projeto.

---

## Pré-requisitos

Certifique-se de ter instalado em sua máquina local:
- Python 3.12+ e `uv` (gerenciador rápido de pacotes Python)
- Node.js 20+ e `npm`
- Docker & Docker Compose
- Git

---

## Passo 1: Clonar o Repositório e Configurar Variáveis de Ambiente

```bash
git clone git@github.com:Rafaelp122/wedding_management.git
cd wedding_management

# Configurar .env no Backend
cp backend/.env.example backend/.env

# Configurar .env no Frontend
cp frontend/.env.example frontend/.env
```

---

## Passo 2: Subir o Banco de Dados (Docker / Neon Local)

```bash
docker compose up -d db
```

---

## Passo 3: Inicializar o Backend Python (Django)

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver 0.0.0.0:8000
```
O backend estará acessível em `http://localhost:8000/api/v1/docs` (OpenAPI Swagger UI).

---

## Passo 4: Inicializar o Frontend React (Vite)

Em outro terminal:
```bash
cd frontend
npm install
npm run dev
```
O frontend estará acessível em `http://localhost:5173`.

---

## Passo 5: Testando a Conexão Fullstack

1. Acesse `http://localhost:5173`.
2. Faça login com as credenciais do superusuário criado no Passo 3.
3. Se o login for bem-sucedido, o dashboard exibirá o contexto do tenant ativo!
