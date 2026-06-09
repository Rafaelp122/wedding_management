# 🔁 Fluxo de CI — Wedding Management System

> **Última atualização:** 9 de junho de 2026

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
              ▼              ▼              ▼
            lint           lint        landing-check
              │              │              │
    ┌─────────┼─────────┐    │              │
    ▼                   ▼    ▼              │
backend-tests    frontend-tests             │
    │                   │                   │
    └───────┬───────────┘                   │
            ▼                               │
      contract-sync                         │
            │                               │
    ┌───────┴───────┐                       │
    ▼               ▼                       ▼
deploy          deploy-frontend        deploy-landing
(Cloud Run)     (Vercel)              (Vercel)
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
| Backend | Ruff | `ruff check . && ruff format --check .` |
| Backend | mypy | `mypy . --show-error-codes` |
| Frontend | ESLint + tsc | `npm run lint && npm run type-check` |

**Condição:** Roda se `backend == true` ou `frontend == true`.

### 2.3 `backend-tests`
**Propósito:** Testes unitários + integridade de migrations.

```bash
python manage.py check                          # Django system checks
python manage.py makemigrations --check --dry-run  # Detecta migrations faltantes
python manage.py migrate --noinput              # Aplica migrations no SQLite
pytest --cov=apps --cov-report=term --cov-report=xml
```

**Ambiente:** `DJANGO_SETTINGS_MODULE=config.settings.test` (SQLite em memória).

**Condição:** Roda se `backend == true` e `lint` passou.

### 2.4 `frontend-tests`
**Propósito:** Testes unitários com Vitest + React Testing Library.

```bash
npm ci && npm run test:ci
```

**Condição:** Roda se `frontend == true` e `lint` passou.

### 2.5 `landing-check`
**Propósito:** Verifica build da landing page Astro.

```bash
npx astro check && npm run build
```

**Condição:** Roda se `landing == true`.

### 2.6 `contract-sync`
**Propósito:** **Valida que o contrato OpenAPI está sincronizado com os hooks Orval.** Não gera código — apenas detecta divergências.

```bash
# Gera openapi.json a partir dos endpoints Django Ninja
python manage.py export_openapi_schema --api config.api.api --output ../openapi.json

# Regenera hooks Orval no frontend
cd frontend && npm ci && npm run generate:api

# Se houver diff, falha
git diff --exit-code || (echo "❌ SCHEMA DESATUALIZADO" && exit 1)
```

**Dependências:** `detect-changes`, `lint`.

> **Decisão de design (ADR implícito):** `contract-sync` depende apenas de `lint`, não de `backend-tests` ou `frontend-tests`. Motivos:
> - O job é um **validador de contrato**, não um gate de qualidade de código — precisa só do código presente e sintaticamente válido.
> - Quando um dos testes é skipped (ex: PR só de backend → `frontend-tests` skipped), o GitHub Actions força o skip de qualquer job que tenha ele em `needs`, bloqueando deploys.
> - Os testes como gate de deploy são aplicados nos jobs de deploy (`deploy` depende de `backend-tests`, `deploy-frontend` depende de `frontend-tests`), não no `contract-sync`.

**Condição:** Roda se `backend == true` ou `frontend == true`, e `lint` passou.

### 2.7 `deploy` (Cloud Run)
**Propósito:** Deploy do backend no Google Cloud Run.

| Evento | Comportamento |
|--------|--------------|
| `pull_request` | Apenas build do Docker (`docker build`) — valida que a imagem compila |
| `push` na `main` | Deploy real via `gcloud run deploy` |

**Dependências:** `detect-changes`, `contract-sync`.

**Condição:** Roda se `backend == true` e jobs anteriores passaram.

### 2.8 `deploy-frontend` (Vercel)
**Propósito:** Deploy do frontend React no Vercel.

| Evento | Comportamento |
|--------|--------------|
| `pull_request` | Preview deploy |
| `push` na `main` | Deploy de produção (`--prod`) |

**Dependências:** `detect-changes`, `contract-sync`.

**Condição:** Roda se `frontend == true` e jobs anteriores passaram.

### 2.9 `deploy-landing` (Vercel)
**Propósito:** Deploy da landing page Astro no Vercel.

**Dependências:** `detect-changes`, `landing-check`.

**Condição:** Roda se `landing == true` e `landing-check` passou.

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

**Solução aplicada:** `contract-sync` agora depende de `lint` (que sempre roda quando backend ou frontend mudam) em vez de `backend-tests` e `frontend-tests`. Os testes seguem como gate nos jobs de deploy individuais.

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

**Causa corrigida** (ver seção 3). Se ocorrer novamente, verifique se `lint` ou `detect-changes` falhou.

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
# 1. Antes de push, rode localmente
cd backend && make lint         # ruff + mypy
cd frontend && npm run lint && npm run type-check

# 2. Se mexeu em API ou modelos
make sync-api                  # Regenera openapi.json + hooks Orval

# 3. Commit e push
git add .
git commit -m "feat(scope): descrição"
git push

# 4. Monitore o CI no GitHub
# Verifique: lint → tests → contract-sync → deploy preview
```
