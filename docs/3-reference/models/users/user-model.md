---
title: "Modelo de Usuário"
domain: users
type: model-reference
code: backend/apps/users/models.py
tests: backend/apps/users/tests/test_models.py
---

# Referência do Modelo: User (Custom User Model)

> **Módulo:** [users-domain](../../../4-explanation/domains/users-domain.md) | [auth-jwt-flow](../../../4-explanation/architecture/auth-jwt-flow.md)
> **Código:** `backend/apps/users/models.py`

---

## Estrutura do Modelo `User`

Herda de `AbstractBaseUser` e `PermissionsMixin`. Utiliza o e-mail como `USERNAME_FIELD`.

### Campos:
- `id`: BigAutoField (PK)
- `uuid`: UUIDField (unique=True, db_index=True) — Identificador público único.
- `email`: EmailField (unique=True, max_length=255) — Campo de autenticação.
- `company`: ForeignKey (`tenants.Company`, on_delete=PROTECT, related_name="users") — Pertencimento a tenant.
- `first_name`: CharField(max_length=150) — Primeiro nome.
- `last_name`: CharField(max_length=150) — Sobrenome.
- `is_staff`: BooleanField (default=False) — Acesso ao admin Django.
- `is_active`: BooleanField (default=False) — Status de ativação da conta.
- `date_joined`: DateTimeField (default=timezone.now) — Data de cadastro.
- `created_at` / `updated_at`: DateTimeField — Timestamps de auditoria do registro.

---

## Regras do `CustomUserManager`

- `_create_user`: Normaliza o e-mail. Se a empresa (`company`) não for fornecida, auto-cria um workspace tenant via `TenantService.create_company(display_name)`.
- `create_user`: Cria usuário inativo por padrão (`is_active=False`).
- `create_superuser`: Cria usuário ativo vinculado ao Workspace Administrativo (`admin-workspace`).
- `make_random_password`: Gera senhas aleatórias seguras para logins sociais.
