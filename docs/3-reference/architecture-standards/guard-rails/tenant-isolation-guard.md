# Especificação Técnica: Guard-Rail de Isolação Multitenant

> **Módulo:** [guard-rails](index.md) | [multi-tenancy-strategy](../../../4-explanation/architecture/multi-tenancy-strategy.md)
> **Teste:** `backend/apps/core/tests/test_tenant_isolation.py`

---

## 1. Visão Geral

O guard-rail **`test_tenant_isolation.py`** audita metaprogramaticamente os modelos e consultas ORM para garantir que todas as consultas em modelos pertencentes a empresas utilizem obrigatoriamente o gerenciador `TenantManager` (`for_tenant(company)`).

---

## 2. Garantias do Teste

1. **Modelos Tenant**: Valida se modelos herdados de `TenantModel` expõem o manager `for_tenant`.
2. **Prevenção de Leaks Cross-Tenant**: Testa se requisições HTTP passando IDs de recursos de outros tenants retornam estritamente `404 Not Found`.
3. **Auditoria de `company` no Service Layer**: Valida se todas as funções públicas em `services.py` recebem o parâmetro `company` (auditado via `test_security_audit.py`).
