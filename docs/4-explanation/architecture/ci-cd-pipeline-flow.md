# 🔁 Fluxo de CI/CD — Wedding Management System

> **Última atualização:** 1 de agosto de 2026

---

## 1. Visão Geral

O pipeline de CI (`integrity-ci.yml`) é acionado em eventos de `push` e `pull_request` na branch `main`. Ele detecta quais partes do monorepo mudaram (backend, frontend ou landing page) e executa os jobs de validação e testes necessários de forma paralela e otimizada.

O pipeline utiliza **Composite Actions** nativas (`.github/actions/`) para abstrair a inicialização dos ambientes Python/UV e Node/PNPM e gerenciar o cache de dependências de forma padronizada.

```text
                         detect-changes & docs-lint
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
            backend?             frontend?             landing?
                │                    │                    │
          ┌─────┴─────┐        ┌─────┼─────┐              │
          ▼           ▼        ▼     ▼     ▼              ▼
        lint      backend-   lint  front-  e2e-        landing-
                   tests           end-   tests         check
          │           │        │   tests   │              │
          │           │        │     │     │              │
          │           └────────┼─────┼─────┘              │
          │                    │     │                    │
          ▼                    ▼     ▼                    │
    contract-sync        contract-sync                    │
          │                    │                          │
          └───────────┬────────┘                          │
                      │        │                          │
                      ▼        ▼                          ▼
                   deploy  deploy-frontend          deploy-landing
                (Cloud Run)  (Vercel)                 (Vercel)

    review ── needs: backend-tests, frontend-tests, landing-check
    (AI Code Review, gate: !failure() && !cancelled())
```

---

## 2. Abstrações de Ambiente (Composite Actions)

Para eliminar a duplicação de boilerplate e garantir caching consistente entre os jobs, o pipeline consome duas ações compostas:

1. **`setup-python-uv` (`.github/actions/setup-python-uv/`)**:
   - Inicializa Python 3.12 via `astral-sh/setup-uv@v5`.
   - Ativa o cache automático baseado em `backend/uv.lock`.
2. **`setup-node-pnpm` (`.github/actions/setup-node-pnpm/`)**:
   - Inicializa PNPM 9.15.0 via `pnpm/action-setup@v4`.
   - Inicializa o Node.js lendo o `.nvmrc` do diretório alvo (`working-directory`).
   - Gerencia o cache de `node_modules` com chave hash baseada em `pnpm-lock.yaml`.
   - Executa `pnpm install --frozen-lockfile` apenas em caso de cache miss.

---

## 3. Detalhamento dos Jobs

### 3.1 `detect-changes`
**Propósito:** Usa `dorny/paths-filter@v3` para determinar os escopos modificados no commit/PR. Outputs: `backend`, `frontend`, `landing`.

**Filtros:**
- `backend`: Mudanças em `backend/**` ou no próprio `integrity-ci.yml`.
- `frontend`: Mudanças em `frontend/**` ou no próprio `integrity-ci.yml`.
- `landing`: Mudanças em `landing/**` ou no próprio `integrity-ci.yml`.

### 3.2 `docs-lint`
**Propósito:** Executa o script `scripts/validate_docs_links.py` para garantir que todos os links internos de documentação e anotações atômicas permaneçam válidos.

### 3.3 `lint`
**Propósito:** Análise estática e checagem de tipos nas áreas modificadas.

| Escopo | Ferramenta | Comando |
|--------|-----------|---------|
| Backend | Ruff | `cd backend && uv run ruff check . && uv run ruff format --check .` |
| Backend | mypy | `cd backend && uv run mypy . --show-error-codes --no-color-output` |
| Frontend | Oxlint + tsc | `cd frontend && pnpm run lint && pnpm run type-check` |

### 3.4 `backend-tests`
**Propósito:** Validação de integridade do Django (migrations, check) e suíte Pytest com cobertura.

```bash
cd backend
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py migrate --noinput
uv run pytest --cov=apps --cov-report=term --cov-report=xml -v
```

### 3.5 `frontend-tests`
**Propósito:** Testes unitários com Vitest e React Testing Library, além da validação de isolamento de mocks da API (`check-api-mock-isolation`).

```bash
cd frontend
pnpm run test:ci
```

### 3.6 `e2e-tests`
**Propósito:** Testes de ponta a ponta com Playwright em matriz dividida em shards (1/2 e 2/2). Sobe o servidor Django local (`runserver 8000`) alimentado por `seed_db`.

### 3.7 `landing-check`
**Propósito:** Validação de checagem de tipos Astro (`astro check`) e build da landing page.
- **Node:** Configurado automaticamente pelo `.nvmrc` da pasta `landing/` (`24.18.0`).

```bash
cd landing
pnpm exec astro check
pnpm run build
```

### 3.8 `contract-sync`
**Propósito:** Garante que o schema OpenAPI exportado pelo backend (`config.api.api`) esteja 100% em sintonia com os hooks gerados pelo Orval no frontend.

```bash
cd backend && uv run python manage.py export_openapi_schema --api config.api.api --output ../openapi.json --indent 2
cd ../frontend && pnpm run generate:api
git diff --exit-code || (echo "❌ SCHEMA DESATUALIZADO. Rode 'make sync-api' localmente." && exit 1)
```

### 3.9 `deploy` (Backend GCP Cloud Run & Artifact Registry)
**Propósito:** Compilação da imagem OCI de produção e deploy imutável no Google Cloud Run.

| Evento | Comportamento |
|--------|--------------|
| `pull_request` | Teste de compilação da imagem OCI via `docker/build-push-action@v6` com `push: false` e cache de camadas (`type=gha`). |
| `push` na `main` | Autenticação OAuth2 no GCP via WIF (`google-github-actions/auth@v2` + `docker/login-action@v3`), push da imagem com tag `$GITHUB_SHA` para o Google Artifact Registry (`us-central1-docker.pkg.dev`), execução de migrations e deploy no Cloud Run apontando para a imagem OCI imutável (`--image`). |


### 3.10 `deploy-frontend` & `deploy-landing` (Vercel)
**Propósito:** Deploy do aplicativo React e da Landing Page no Vercel (Preview em PRs, Produção em pushes na branch `main`).

### 3.11 `review` (AI Code Review)
**Propósito:** Revisão automatizada estática em PRs via OpenCode (modelo DeepSeek). Possui guard por label `ai-reviewed` para evitar execuções redundantes.

---

## 4. Troubleshooting & Soluções Comuns

### `contract-sync` falhou com "SCHEMA DESATUALIZADO"
**Causa:** O arquivo `openapi.json` ou os hooks em `frontend/src/api/generated/` estão desalinhados em relação aos endpoints Django.

**Solução:**
```bash
make sync-api
git add openapi.json frontend/src/api/generated/
git commit -m "chore(api): sync OpenAPI schema and Orval hooks"
```

### `makemigrations --check` falhou
**Causa:** Foi feita uma alteração em modelos Django sem gerar a migration correspondente.

**Solução:**
```bash
cd backend
uv run python manage.py makemigrations
git add apps/*/migrations/*.py
git commit -m "fix(backend): add missing migration"
```

---

## 5. Workflow do Desenvolvedor

```bash
# 1. Antes de enviar push, execute a verificação local
make lint                      # ruff + mypy (backend) + oxlint + tsc (frontend)

# 2. Se alterou APIs ou modelos
make sync-api                  # export_openapi_schema + hooks Orval

# 3. Valide a documentação e anotações atômicas
make check-docs

# 4. Commit e push
git add .
git commit -m "feat(scope): descrição da feature"
git push
```

---

## 6. ADRs Relacionados

- [ADR-006: Service Layer Architecture](../adr/006-service-layer.md) — Separação entre endpoints e lógica de negócio.
- [ADR-011: BaseModel e Validação em Save](../adr/011-basemodel-save-full-clean.md) — Regra de integridade do modelo Django.
- [ADR-012: Orval Contract-Driven Frontend](../adr/012-orval-contract-driven-frontend.md) — Geração estritamente tipada de hooks a partir do OpenAPI schema (`contract-sync`).
- [ADR-013: Migração DRF para Django Ninja](../adr/013-migrate-drf-to-ninja.md) — Escolha do framework de API com schema OpenAPI embutido.
- [ADR-018: Playwright E2E Testing](../adr/018-playwright-e2e-testing.md) — Testes de ponta a ponta em sharding no CI.
- [ADR-021: Padrão de Comentários e Docstrings](../adr/021-padrao-comentarios-docstrings.md) — Diretrizes de documentação de código.
