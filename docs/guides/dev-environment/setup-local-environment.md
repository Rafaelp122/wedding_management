# Como Configurar o Ambiente de Desenvolvimento Local

> **Categoria:** [dev-environment](index.md) | [database-migrations](database-migrations.md) | [seed-database](../backend/seed-database.md)
> **Comandos Principais:** `make setup`, `make up`, `make dev`, `make frontend-dev`, `make seed-db`

---

## Visão Geral

Este guia prático orienta a configuração passo a passo do ambiente de desenvolvimento local do **Wedding Management System (WMS)**. O sistema suporta duas modalidades de execução:
1. **Modalidade Híbrida (Recomendada):** Banco de dados e Backend isolados em **Docker Compose**, com Frontend SPA e Landing Page rodando no **Host**.
2. **Modalidade Host Local Puro:** Todos os serviços rodando diretamente na máquina local via gerenciadores de pacotes rápidos (`uv` para Python e `pnpm` para Node.js).

---

## Pré-requisitos

Certifique-se de ter instalado em sua estação de trabalho:

- **Git** 2.40+
- **Docker** 24+ & **Docker Compose** v2+ (para a modalidade Docker)
- **Python** 3.12+ e gerenciador **`uv`** 0.5+ ([Instalação do UV](https://docs.astral.sh/uv/))
- **Node.js** 20+ (LTS) e gerenciador **`pnpm`** 9+ ([Instalação do Pnpm](https://pnpm.io/installation))

---

## Passo 1: Preparar as Variáveis de Ambiente (`.env`)

Na raiz do repositório, execute o alvo do Makefile para provisionar o arquivo `.env` a partir do template canônico:

```bash
make env-setup
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
> make secret-key
> ```

---

## Passo 2: Inicializar os Serviços

### Modalidade A: Docker Compose (Recomendada)

1. **Inicialize os containers do banco de dados e backend:**
   ```bash
   make up
   ```
   *Saída esperada no terminal:*
   ```text
   🚀 Iniciando containers essenciais (db e backend)...
   [+] Running 2/2
    ✔ Container wedding_db       Started
    ✔ Container wedding_backend  Started
   ⏳ Aguardando banco de dados estar pronto...
   Operations to perform:
     Apply all migrations: admin, auth, contenttypes, core, finances, logistics, notifications, scheduler, sessions, tenants, users, weddings
   Running migrations:
     Applying core.0001_initial... OK
     ...
   ✅ Backend pronto!
      Docs/API:  http://localhost:8000/api/v1/docs
   ```

2. **Inicie o servidor de desenvolvimento do Frontend SPA (no Host):**
   ```bash
   make frontend-dev
   ```
   *A interface estará acessível em `http://localhost:5173`.*

3. **(Opcional) Inicie a Landing Page institucional (no Host):**
   ```bash
   make landing-dev
   ```
   *A landing page estará acessível em `http://localhost:4321`.*

---

### Modalidade B: Host Local (UV + Pnpm)

Se preferir rodar todos os binários diretamente sem Docker (com um PostgreSQL local já ativo na porta 5432):

1. **Sincronize as dependências e aplique as migrações no Backend:**
   ```bash
   cd backend
   uv sync --all-groups
   uv run python manage.py migrate
   uv run python manage.py runserver 0.0.0.0:8000
   ```

2. **Instale e execute o Frontend SPA:**
   ```bash
   cd ../frontend
   pnpm install --frozen-lockfile
   pnpm run dev
   ```

---

## Passo 3: Povoar o Banco de Dados (Seeding)

Para trabalhar com dados realistas (casamentos, fornecedores, contratos, despesas parceladas e tarefas):

1. **Popular templates oficiais de cronograma de casamento:**
   ```bash
   # Executa o comando de templates canônicos
   docker compose exec backend python manage.py seed_wedding_templates
   # Ou se estiver no Host local:
   cd backend && uv run python manage.py seed_wedding_templates
   ```

2. **Gerar massa de dados fictícios completos (Faker):**
   ```bash
   docker compose exec backend python manage.py seed_db
   # Ou se estiver no Host local:
   cd backend && uv run python manage.py seed_db
   ```

3. **Criar um superusuário administrativo:**
   ```bash
   make superuser
   ```

---

## Passo 4: Verificação de Saúde e Conectividade

Valide o funcionamento dos serviços acessando as URLs de diagnóstico:

| Teste | URL / Comando | Resultado Esperado |
| :--- | :--- | :--- |
| **API Healthcheck** | `curl -i http://localhost:8000/api/v1/health` | HTTP `200 OK` com `{"status": "healthy"}` |
| **Swagger Interativo** | [`http://localhost:8000/api/v1/docs`](http://localhost:8000/api/v1/docs) | Interface gráfica OpenAPI do Django Ninja |
| **Frontend Web** | [`http://localhost:5173`](http://localhost:5173) | Tela de Login / Dashboard da aplicação |
| **Portal MkDocs** | [`http://localhost:8001`](http://localhost:8001) | Documentação técnica com live-reload |

---

## Troubleshooting & Resolução de Problemas

### 1. Conflito de Porta 5432 (PostgreSQL já em execução no Host)
- **Sintoma:** `Bind for 0.0.0.0:5432 failed: port is already allocated`.
- **Causa:** Um serviço PostgreSQL local já está escutando na porta 5432.
- **Solução:** Pare o PostgreSQL local do sistema operacional (`sudo systemctl stop postgresql`) antes de rodar `make up`, ou altere a porta mapeada no `docker-compose.yml`.

### 2. Erro de Permissão em Arquivos Gerados pelo Docker
- **Sintoma:** Erros de `Permission denied` ao editar arquivos no Host que foram criados dentro do container.
- **Solução:** Execute o utilitário de reparo de permissões:
  ```bash
  make fix-perms
  ```

### 3. Falha de Módulos Node ou Python Desatualizados
- **Sintoma:** `ModuleNotFoundError` no backend ou `Cannot find package` no frontend.
- **Solução:** Ressincronize as dependências com lockfiles estritos:
  ```bash
  # Backend
  make reqs
  # Frontend
  cd frontend && pnpm install --frozen-lockfile
  ```
