# How-To: Configuração de Variáveis .env e Dependências Locais

> **Objetivo:** Resolver problemas comuns de ambiente e configurar o `.env` local.

---

## 1. Configurando Variáveis de Ambiente no Backend

Edite `backend/.env` garantindo que as chaves de banco de dados e JWT estejam definidas:

```env
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-prod
DATABASE_URL=postgres://postgres:postgres@localhost:5432/wedding_db  # pragma: allowlist secret
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

## 2. Re-instalando Dependências com `uv`

Se houver discrepâncias de versão no ambiente Python, limpe e ressincronize o ambiente:

```bash
cd backend
uv sync --frozen
```
