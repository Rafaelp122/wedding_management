# 🔁 Fluxo de CI — Wedding Management System

> **Última atualização:** 13 de junho de 2026

---

## 1. Visão Geral

O pipeline de CI (`integrity-ci.yml`) é acionado em `push` e `pull_request` na branch `main`. Ele detecta quais partes do monorepo mudaram e executa apenas os jobs relevantes, otimizando tempo de CI.

```
                         detect-changes
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
           backend?       frontend?       landing?
               │              │              │
         ┌─────┴─────┐  ┌────┴─────┐        │
         ▼           ▼  ▼          ▼        ▼
       lint      backend-  lint  frontend-  landing-
                  tests          tests      check
         │           │    │         │        │
         └──────┬────┘    └────┬────┘        │
                ▼              ▼              │
          contract-sync        │              │
            │    │             │              │
            │    └──────┐      │              │
            ▼           ▼      ▼              ▼
       deploy         deploy-frontend    deploy-landing
    (Cloud Run)        (Vercel)          (Vercel)
    (needs backend-   (needs frontend-
     tests +           tests +
      contract-sync)    contract-sync)

   review ── needs: backend-tests, frontend-tests, landing-check
   (AI Code Review, gate: bloqueia se testes falharem, roda se skipped)
```

---

## 2. Jobs

### 2.1 `detect-changes`
**Propósito:** Usa `dorny/paths-filter@v3` para detectar quais diretórios mudaram. Outputs: `backend`, `frontend`, `landing`.

**Filtros:**
- `backend`: `backend/**` ou mudanças no próprio `integrity-ci.yml`
- `frontend`: `frontend/**` ou mudanças no próprio `integrity-ci.yml`
- `landing`: `landing/**` ou mudanças no próprio `integrity-ci.yml`

> O `integrity-ci.yml` está em todos os filtros para que alterações no pipeline disparem todos os jobs de validação.

### 2.2 `lint`
**Propósito:** Roda análise estática nas partes que mudaram.

| Stack | Ferramenta | Comando |
|-------|-----------|---------|
| Backend | Ruff | `cd backend && uv run ruff check . && uv run ruff format --check .` |
| Backend | mypy | `cd backend && uv run mypy . --show-error-codes --no-color-output` (precisa de `SECRET_KEY` no env) |
| Frontend | ESLint + tsc | `cd frontend && npm ci && npm run lint && npm run type-check` |

**Condição:** Roda se `backend == true` ou `frontend == true`.

### 2.3 `backend-tests`
**Propósito:** Testes unitários + integridade de migrations + upload de coverage.

```bash
# Django Integrity Check
cd backend
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py migrate --noinput

# Testes com cobertura
uv run pytest --cov=apps --cov-report=term --cov-report=xml -v

# Upload para Codecov (codecov/codecov-action@v5)
```

**Ambiente:** `DJANGO_SETTINGS_MODULE=config.settings.test`, `SECRET_KEY=django-ci-secret-key-not-for-production`.

**Condição:** Roda se `backend == true`.

### 2.4 `frontend-tests`
**Propósito:** Testes unitários com Vitest + React Testing Library + upload de coverage.

```bash
cd frontend && npm ci && npm run test:ci
# Upload para Codecov (codecov/codecov-action@v5)
```

**Condição:** Roda se `frontend == true`.

### 2.5 `landing-check`
**Propósito:** Verifica build da landing page Astro.

```bash
cd landing && npm ci && npx astro check && npm run build
```

**Node:** versão 22.

**Condição:** Roda se `landing == true`.

### 2.6 `contract-sync`
**Propósito:** **Valida que o contrato OpenAPI está sincronizado com os hooks Orval.** Não gera código — apenas detecta divergências.

```bash
# Gera openapi.json a partir dos endpoints Django Ninja
cd backend && uv run python manage.py export_openapi_schema --api config.api.api --output ../openapi.json

# Regenera hooks Orval no frontend
cd ../frontend && npm ci && npm run generate:api

# Se houver diff, falha
git diff --exit-code || (echo "❌ SCHEMA DESATUALIZADO" && exit 1)
```

**Dependências:** `detect-changes`, `lint`.

> **Decisão de design (ADR implícito):** `contract-sync` depende de `lint` (análise estática rápida), não de `backend-tests` ou `frontend-tests`. Motivos:
> - O job é um **validador de contrato**, não um gate de qualidade de código — precisa só do código presente e sintaticamente válido.
> - Quando um dos testes é skipped (ex: PR só de backend → `frontend-tests` skipped), o GitHub Actions força o skip de qualquer job que tenha ele em `needs`, bloqueando deploys.
> - Os testes são gate de deploy diretamente nos jobs de deploy (`deploy` depende de `backend-tests` + `contract-sync`, `deploy-frontend` depende de `frontend-tests` + `contract-sync`).
> - `lint` retém dependência porque é rápido (segundos) e evita que `contract-sync` desperdice minutos buildando/puxando dependências se o código tem erros óbvios.

**Condição:** Roda se `backend == true` ou `frontend == true`, e `lint` passou.

### 2.7 `deploy` (Cloud Run)
**Propósito:** Deploy do backend no Google Cloud Run.

| Evento | Comportamento |
|--------|--------------|
| `pull_request` | Apenas build do Docker (`docker build`) — valida que a imagem compila |
| `push` na `main` | Deploy real via `gcloud run deploy` |

**Dependências:** `detect-changes`, `backend-tests`, `contract-sync`.

**Condição:** Roda se `backend == true` e jobs anteriores passaram.

### 2.8 `deploy-frontend` (Vercel)
**Propósito:** Deploy do frontend React no Vercel.

| Evento | Comportamento |
|--------|--------------|
| `pull_request` | Preview deploy |
| `push` na `main` | Deploy de produção (`--prod`) |

**Dependências:** `detect-changes`, `frontend-tests`, `contract-sync`.

**Condição:** Roda se `frontend == true` e jobs anteriores passaram.

### 2.9 `deploy-landing` (Vercel)
**Propósito:** Deploy da landing page Astro no Vercel.

**Dependências:** `detect-changes`, `landing-check`.

**Condição:** Roda se `landing == true` e `landing-check` passou.

### 2.10 `review` — AI Code Review (dentro do integrity-ci)
**Propósito:** Revisão automatizada de PR via OpenCode + DeepSeek. Verifica desvios arquiteturais, segurança, e qualidade seguindo os skills do projeto.

**Dependências:** `detect-changes`, `backend-tests`, `frontend-tests`, `landing-check`.

**Condição:** Apenas em `pull_request` (não em push na main), quando backend ou frontend mudaram. Bloqueia se algum teste falhar, mas roda normalmente se forem skipped (ex: PR só de backend).

**Fluxo:**
1. Roda automaticamente dentro do pipeline de CI, após testes passarem
2. Verifica se o label `ai-reviewed` já existe na PR — se sim, **skipa**
3. Executa o reviewer via `anomalyco/opencode/github` com `deepseek-v4-pro`
4. Após review bem-sucedido, adiciona o label `ai-reviewed` na PR

**Re-review:** Use `opencode-assistant.yml` — comente `/opencode` na PR para disparar uma nova revisão a qualquer momento.

> **Decisão de design:** Integrado ao integrity-ci para simplificar o pipeline. Usa `needs.<job>.result == 'failure'` em vez de `always() && !failure()` para evitar o edge case onde jobs skipped forçam o skip do review. O label `ai-reviewed` é o guard que impede revisões repetidas em pushes subsequentes.
>
> **Cancelamento em progresso:** Como o integrity-ci tem `concurrency: cancel-in-progress: true`, um novo push cancela o review em andamento. Como o label ainda não foi adicionado (job cancelado antes de completar), o próximo push bem-sucedido rodará o review novamente — garantindo que a versão mais recente seja sempre revisada.

---

## 3. Comportamento GitHub Actions: Jobs Skipped

Um comportamento importante do GitHub Actions: **se um job em `needs` é skipped, o job dependente é automaticamente skipped**, independente da condição `if`.

Exemplo:
```yaml
contract-sync:
    needs: [detect-changes, backend-tests, frontend-tests]
    if: success() && needs.detect-changes.outputs.backend == 'true'
```

Se `frontend-tests` é skipped (sem mudanças no frontend), `contract-sync` é forçado a skip também, mesmo com `backend == true` e `backend-tests` tendo passado. Isso quebrava deploys em PRs só de backend.

**Solução aplicada:** `contract-sync` depende de `lint` (rápido, segundos) em vez de `backend-tests` e `frontend-tests`. Os testes rodam em paralelo com `lint` (mesmo nível, sem dependência) e servem como gate nos jobs de deploy individuais.

---

## 4. Troubleshooting

### `contract-sync` falhou com "SCHEMA DESATUALIZADO"

**Causa:** O `openapi.json` commitado está desatualizado em relação aos endpoints Django, ou os hooks Orval não foram regenerados.

**Solução:**
```bash
# Gere localmente
make sync-api

# Verifique o diff
git diff

# Commit as mudanças
git add openapi.json frontend/src/api/generated/
git commit -m "chore(api): sync OpenAPI schema and Orval hooks"
```

### Deploy pulado em PR só de backend

**Causa corrigida** (ver seção 3). Se ocorrer novamente, verifique se `lint`, `backend-tests` ou `detect-changes` falhou.

### `makemigrations --check` falhou

**Causa:** Alteração no modelo Django sem migration correspondente.

**Solução:**
```bash
cd backend
uv run python manage.py makemigrations
git add apps/*/migrations/*.py
git commit -m "fix(backend): add missing migration for <model>.<field>"
```

---

## 5. Workflow no Desenvolvedor

```bash
# 1. Antes de push, rode localmente (necessário Docker rodando)
make lint                      # ruff + mypy (backend) + ESLint + tsc (frontend)

# 2. Se mexeu em API ou modelos
make sync-api                  # export_openapi_schema + orval hooks

# 3. Commit e push
git add .
git commit -m "feat(scope): descrição"
git push

# 4. Monitore o CI no GitHub
# Verifique: lint + tests (paralelo) → contract-sync → deploy preview
```
