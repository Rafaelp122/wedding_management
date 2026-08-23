# How-To: Executando Migrations de Banco de Dados com Segurança

> **Objetivo:** Criar e aplicar migrations do Django sem violar restrições de Multi-tenancy ou BaseModel.

---

## 1. Criar Migrations Após Alterações nos Models

```bash
cd backend
uv run python manage.py makemigrations
```

---

## 2. Inspecionar a Migration Gerada

Abra a nova migration em `backend/apps/<modulo>/migrations/XXXX_....py` e verifique:
- Se novos campos `NOT NULL` contêm valor padrão (`default=...`).
- Se chaves estrangeiras para tenant possuem `on_delete=models.PROTECT`.

---

## 3. Aplicar Migrations no Banco

```bash
uv run python manage.py migrate
```
