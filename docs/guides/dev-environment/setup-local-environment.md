# Como Configurar o Ambiente de Desenvolvimento Local

> **Categoria:** [dev-environment](index.md) | [task-runner-just](task-runner-just.md) | [database-migrations](database-migrations.md) | [seed-database](../backend/seed-database.md)
> **Comandos Principais:** `just setup`, `just up`, `just dev`, `just frontend-dev`, `just seed-db`

---

## Visão Geral

Este guia prático orienta a configuração passo a passo do ambiente de desenvolvimento local do **Wedding Management System (WMS)**. O sistema suporta duas modalidades de execução:
1. **Modalidade Híbrida (Recomendada):** Banco de dados e Backend isolados em **Docker Compose**, com Frontend SPA e Landing Page rodando no **Host**.
2. **Modalidade Host Local Puro:** Todos os serviços rodando diretamente na máquina local via gerenciadores de pacotes rápidos (`uv` para Python e `pnpm` para Node.js).

Você pode orquestrar todas as operações utilizando o task runner **`just`** ou executar diretamente os **comandos nativos** das ferramentas subjacentes.

---

## Pré-requisitos

Certifique-se de ter instalado em sua estação de trabalho:

- **Git** 2.40+
- **`just`** 1.35+ (Opcional / Recomendado — [Guia do Task Runner Just](task-runner-just.md))
- **Docker** 24+ & **Docker Compose** v2+ (para a modalidade Docker)
- **Python** 3.12+ e gerenciador **`uv`** 0.5+ ([Instalação do UV](https://docs.astral.sh/uv/))
- **Node.js** 20+ (LTS) e gerenciador **`pnpm`** 9+ ([Instalação do Pnpm](https://pnpm.io/installation))

---

## Passo 1: Preparar as Variáveis de Ambiente (`.env`)

Na raiz do repositório, provisione o arquivo `.env` a partir do template canônico:

```bash
# Via Just (Recomendado):
just env-setup

# Ou Trilha Nativa Direta:
python3 -c "import os, shutil; shutil.copyfile('.env.example', '.env') if not os.path.exists('.env') else None"
```

Caso o arquivo `.env` já exista, revise suas configurações críticas:

```env
# Configurações de Execução do Django
DEBUG=True
SECRET_KEY=dev-insecure-secret-key-for-local-testing-only-1234567890
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Conexão com o PostgreSQL Local
DATABASE_URL=postgres://wedding_user:wedding_pass@localhost:5432/wedding_db  # pragma: allowlist secret
DB_USER=wedding_user
DB_PASSWORD=wedding_pass  # pragma: allowlist secret
DB_NAME=wedding_db

# CORS e Comunicação com o Frontend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4321
FRONTEND_URL=http://localhost:5173

# Cloudflare R2 Mock / Storage Local (Presigned URLs)
CLOUDFLARE_R2_BUCKET_NAME=wedding-management-local-dev
CLOUDFLARE_R2_ENDPOINT_URL=https://dummy.r2.cloudflarestorage.com
```

> [!TIP]
> Para gerar uma nova chave criptográfica `SECRET_KEY` aleatória para o `.env`, execute:
> ```bash
> # Via Just:
> just secret-key
>
> # Ou Trilha Nativa:
> python -c "import secrets; print(secrets.token_urlsafe(50))"
> ```

---

## Passo 2: Inicializar os Serviços

### Modalidade A: Docker Compose + Host (Recomendada)

1. **Inicialize os containers do banco de dados e backend com migrações aplicadas:**
   ```bash
   # Via Just:
   just up

   # Ou Trilha Nativa Direta:
   docker compose up -d backend && docker compose exec backend uv run poe migrate
   ```
   *Saída esperada no terminal:*
   ```text
   🚀 Iniciando containers essenciais (db e backend)...
   [+] Running 2/2
    ✔ Container wedding_db       Started
    ✔ Container wedding_backend  Started
   🔄 Aplicando migrações...
   Operations to perform:
     Apply all migrations: admin, auth, contenttypes, core, finances, logistics, notifications, scheduler, sessions, tenants, users, weddings
   Running migrations:
     Applying core.0001_initial... OK
     ...
   ✅ Backend pronto em http://localhost:8000/api/v1/docs
   ```

2. **(Opcional) Acompanhe os logs dos containers em tempo real:**
   ```bash
   # Via Just:
   just dev

   # Ou Trilha Nativa:
   docker compose logs -f backend db
   ```

3. **Inicie o servidor de desenvolvimento do Frontend SPA (no Host):**
   ```bash
   # Via Just:
   just frontend-dev

   # Ou Trilha Nativa:
   cd frontend && pnpm run dev
   ```
   *A interface estará acessível em `http://localhost:5173`.*

4. **(Opcional) Inicie a Landing Page comercial (no Host):**
   ```bash
   # Via Just:
   just landing-dev

   # Ou Trilha Nativa:
   cd landing && pnpm run dev
   ```
   *A landing page estará acessível em `http://localhost:4321`.*

---

### Modalidade B: Host Local Puro (UV + Pnpm)

Se preferir rodar todos os binários diretamente sem Docker para o backend (com um PostgreSQL local ou container de banco ativo na porta 5432):

1. **Suba apenas o container de banco de dados:**
   ```bash
   docker compose up -d db
   ```

2. **Sincronize as dependências e aplique as migrações no Backend:**
   ```bash
   cd backend
   uv sync --all-groups
   uv run poe migrate
   uv run python manage.py runserver 0.0.0.0:8000
   ```

3. **Instale e execute o Frontend SPA:**
   ```bash
   cd frontend
   pnpm install --frozen-lockfile
   pnpm run dev
   ```

---

## Passo 3: Povoar o Banco de Dados (Seeding)

Para trabalhar com dados realistas (casamentos, fornecedores, contratos, despesas parceladas e tarefas):

1. **Popular massa de dados determinística para testes E2E:**
   ```bash
   # Via Just:
   just seed-e2e

   # Ou Trilha Nativa no Container:
   docker compose exec backend uv run poe seed-e2e

   # Ou no Host Local:
   cd backend && uv run poe seed-e2e
   ```

2. **Gerar massa de dados fictícios completos (Faker):**
   ```bash
   # Via Just:
   just seed-db

   # Ou Trilha Nativa no Container:
   docker compose exec backend uv run poe seed-db

   # Ou no Host Local:
   cd backend && uv run poe seed-db
   ```

3. **Criar um superusuário administrativo:**
   ```bash
   # Via Just:
   just superuser

   # Ou Trilha Nativa no Container:
   docker compose exec backend uv run poe superuser

   # Ou no Host Local:
   cd backend && uv run poe superuser
   ```

---

## Passo 4: Verificação de Saúde e Conectividade

Valide o funcionamento dos serviços acessando as URLs de diagnóstico:

| Teste | URL / Comando | Trilha `just` | Trilha Nativa | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| **API Healthcheck** | `curl -i http://localhost:8000/api/v1/health` | — | `curl -i http://localhost:8000/api/v1/health` | HTTP `200 OK` com `{"status": "healthy"}` |
| **Swagger Interativo** | [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs) | `just up` / `just dev` | `docker compose up -d backend` | Interface gráfica OpenAPI do Django Ninja |
| **Frontend Web** | [`http://localhost:5173`](http://localhost:5173) | `just frontend-dev` | `cd frontend && pnpm run dev` | Tela de Login / Dashboard da aplicação |
| **Portal MkDocs** | [`http://localhost:8001`](http://localhost:8001) | `just docs-dev` | `uv run --project backend --group docs mkdocs serve -a 0.0.0.0:8001` | Documentação técnica com live-reload |

---

## Troubleshooting & Resolução de Problemas

### 1. Conflito de Porta 5432 (PostgreSQL já em execução no Host)
- **Sintoma:** `Bind for 0.0.0.0:5432 failed: port is already allocated`.
- **Causa:** Um serviço PostgreSQL local já está escutando na porta 5432.
- **Solução:** Pare o PostgreSQL local do sistema operacional (`sudo systemctl stop postgresql`) antes de rodar `just up`, ou altere a porta mapeada no `docker-compose.yml`.

### 2. Reset Completo do Banco de Dados Local
- **Sintoma:** Estado inconsistente nas tabelas ou necessidade de recomeçar do zero.
- **Solução:** Execute o reset do banco para recriar os volumes e reaplicar as migrações:
  ```bash
  # Via Just:
  just db-reset

  # Ou Trilha Nativa:
  docker compose down -v db && docker compose up -d backend && docker compose exec backend uv run poe migrate
  ```

### 3. Falha de Módulos Node ou Python Desatualizados
- **Sintoma:** `ModuleNotFoundError` no backend ou `Cannot find package` no frontend.
- **Solução:** Ressincronize as dependências com lockfiles estritos:
  ```bash
  # Backend:
  just reqs
  # (Trilha Nativa: cd backend && uv lock)

  # Frontend:
  cd frontend && pnpm install --frozen-lockfile
  ```
