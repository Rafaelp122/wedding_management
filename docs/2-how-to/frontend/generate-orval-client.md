# How-To: Sincronização de Contratos OpenAPI -> Orval/Zod

> **Objetivo:** Atualizar os hooks TypeScript gerados automaticamente a partir dos endpoints Django Ninja.

---

## Passo a Passo

1. **Certifique-se de que o backend está rodando:**
   ```bash
   cd backend
   uv run python manage.py runserver
   ```
2. **Execute a geração do cliente Orval no frontend:**
   ```bash
   cd frontend
   npm run api:generate
   ```
3. **Validar arquivos gerados:**
   Confira se os arquivos em `frontend/src/api/generated/` foram atualizados com os novos hooks e schemas.
