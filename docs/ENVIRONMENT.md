# 🔧 Guia de Configuração de Ambiente

Este documento é um **How-to Guide** que descreve como preparar, rodar e manter o ambiente de desenvolvimento do Wedding Management System.

---

## 🏗️ Opção 1: Rodando com Docker (Recomendado)

O Docker garante que o banco de dados, o backend e o frontend rodem em um ambiente isolado idêntico à produção.

### Passo 1: Configurar Variáveis
```bash
cp .env.example .env
make secret-key  # Adicione o valor gerado em SECRET_KEY no seu .env
```

### Passo 2: Subir os Containers
```bash
make up
```

### Passo 3: Migrar e Iniciar Dados
```bash
make migrate
make superuser
```

---

## 💻 Opção 2: Rodando Localmente (Bare Metal)

Útil para desenvolvimento focado em debugging ou quando você não quer usar Docker.

### Backend (Python)
Requer `uv` instalado ([instalar uv](https://github.com/astral-sh/uv)).
```bash
cd backend
uv sync --group dev
uv run python manage.py migrate
uv run python manage.py runserver
```

### Frontend (Node)
```bash
cd frontend
npm ci
npm run dev
```

---

## 📋 Referência de Comandos (Makefile)

O projeto utiliza um `Makefile` para automatizar tarefas repetitivas.

| Comando | Descrição |
|---|---|
| `make up` | Inicia todos os serviços via Docker. |
| `make down` | Para e remove os containers. |
| `make logs` | Exibe logs de todos os serviços. |
| `make migrate` | Aplica as migrações do banco de dados. |
| `make test` | Executa a suíte de testes com Pytest. |
| `make lint` | Executa o linter e formatter (Ruff). |
| `make check-ci` | Executa o gate completo de qualidade (Lint + Mypy + Testes). |
| `make sync-api` | Sincroniza o contrato OpenAPI e regera o cliente Frontend (Orval). |

---

## 🔐 Variáveis de Ambiente (.env)

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | - | Chave de segurança do Django. |
| `DEBUG` | `True` | Ativa o modo debug do Django. |
| `DB_HOST` | `db` | Host do banco (use `localhost` se rodar fora do Docker). |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Origens permitidas para o Frontend. |

---

## 🆘 Troubleshooting Comum

### 1. Erro de Conexão com o Banco
Se você vir `connection refused`, certifique-se de que o container `db` está UP:
```bash
docker compose ps
```

### 2. Mudanças no Banco não Refletidas
Se você alterou um modelo, lembre-se de gerar e aplicar as migrações:
```bash
make makemigrations
make migrate
```

### 3. Frontend não encontra a API
Verifique se a variável `VITE_API_URL` no frontend aponta para a porta correta (geralmente `http://localhost:8000`).

---

**Dúvidas técnicas?** Consulte o documento de **[Arquitetura](ARCHITECTURE.md)**.
