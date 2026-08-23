# Arquitetura: Estratégia de Multi-Tenancy

> **Módulo:** [multi-tenancy-strategy](multi-tenancy-strategy.md) | [tenants-domain](../domains/tenants-domain.md)
> **ADRs de Referência:** ADR-009, ADR-016, ADR-019

---

## Visão Geral

O sistema adota uma abordagem de **Multi-tenancy Pragmático** em um único banco de dados (Shared Database, Shared Schema) com isolamento estrito por coluna de chave estrangeira (`company_id`).

---

## Camada de Backend

1. **Entidade Root (`Company`):** Toda assessoria de eventos cadastrada é representada por uma `Company`.
2. **Modelos Herdando de `TenantModel`:** Toda entidade de domínio herda de `TenantModel`, que injeta a `ForeignKey("tenants.Company", on_delete=PROTECT)`.
3. **`TenantManager` / `for_tenant`:** O ORM proíbe queries globais desprotegidas. Os serviços sempre utilizam `Model.objects.for_tenant(company)`.
4. **Validação na Service Layer (ADR-019):** A camada de serviço recebe explicitamente a `company` ativa e valida o pertencimento de todos os objetos antes de qualquer mutação.

---

## Camada de Frontend

1. **Token JWT:** O `company_id` está codificado nas reivindicações (*claims*) do token JWT do usuário autenticado.
2. **Filtragem no Contexto:** A aplicação recupera e ajusta automaticamente a empresa ativa no login através do `useAuthStore`, garantindo que os dados visualizados no dashboard pertençam estritamente ao tenant atual.
