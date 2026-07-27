# Especificação Técnica: Dicionário de Variáveis de Ambiente (.env)

> **Módulo:** [dev-environment](../../2-how-to/dev-environment/index.md) | [system-overview](../../4-explanation/architecture/system-overview.md)
> **Arquivos:** `backend/.env.example`, `frontend/.env.example`

---

## Backend Environment Variables (`backend/.env`)

| Variável | Tipo | Requerida | Padrão | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `DEBUG` | boolean | Sim | `False` | Habilita modo debug do Django. |
| `SECRET_KEY` | string | Sim | - | Chave secreta de criptografia e assinaturas de sessão/JWT. |
| `ALLOWED_HOSTS` | string | Sim | `localhost,127.0.0.1` | Lista separada por vírgula de hosts permitidos. |
| `DATABASE_URL` | string | Sim | - | String de conexão PostgreSQL (PostgreSQL Neon). |
| `CORS_ALLOWED_ORIGINS` | string | Sim | `http://localhost:5173` | Origens aceitas para CORS. |
| `R2_ACCOUNT_ID` | string | Não | - | Account ID do Cloudflare R2 para upload S3. |
| `R2_ACCESS_KEY_ID` | string | Não | - | Access Key ID para buckets R2. |
| `R2_SECRET_ACCESS_KEY` | string | Não | - | Secret Access Key do Cloudflare R2. |
| `R2_BUCKET_NAME` | string | Não | - | Nome do bucket de arquivos/mídia. |
| `NINJA_JWT_ACCESS_EXPIRATION_MINUTES` | int | Sim | `60` | Tempo de expiração do Access Token JWT. |
| `NINJA_JWT_REFRESH_EXPIRATION_DAYS` | int | Sim | `7` | Tempo de expiração do Refresh Token JWT. |

---

## Frontend Environment Variables (`frontend/.env`)

| Variável | Tipo | Requerida | Padrão | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `VITE_API_URL` | string | Sim | `http://localhost:8000` | URL base do backend Django Ninja. |
| `VITE_APP_NAME` | string | Não | `Wedding Management` | Nome exibido da aplicação. |
