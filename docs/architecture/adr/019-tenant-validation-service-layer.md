# ADR-019: Validação de Tenant na Camada de Serviço

## Status
Aceito

## Contexto
A arquitetura de multi-tenancy do sistema (ADR-009, ADR-016) isola os dados verticalmente por `Company` através do `TenantManager` com `.for_tenant(company)` nas queries do banco. No entanto, diversos métodos da camada de serviço (`update()`, `delete()`, `mark_as_paid()`, etc.) recebem uma instância do modelo já carregada — seja pela API (que faz `get()` antes de chamar o service) ou por chamadas internas entre services.

Nesses métodos, o parâmetro `company` era recebido mas **nunca validado contra a instância**. Um chamador da API está protegido pelo `get()` na camada de API, mas uma chamada interna entre services (ou um erro na camada de API) poderia operar em uma instância de outro tenant silenciosamente.

## Decisão
Criar um helper centralizado `validate_tenant_ownership()` que verifica se `instance.company_id == company.id`, levantando `ObjectNotFoundError` (HTTP 404) em caso de mismatch. Aplicar em **todo método que recebe uma instância pré-carregada**.

### Por que 404 e não 403?
Retornar 403 ("acesso negado") revelaria ao atacante que o recurso existe em outro tenant. Com 404, os casos "recurso não existe" e "recurso existe em outro tenant" são indistinguíveis — prática padrão em SaaS multi-tenant.

### Helper centralizado
```python
def validate_tenant_ownership(company, instance, *, detail, code):
    if instance.company_id != company.id:
        raise ObjectNotFoundError(detail=detail, code=code)
```

### Escopo de aplicação
Todos os métodos dos 10 services que recebem `(company, instance, ...)`:
- `delete()` — 10 services
- `update()` — 8 services
- `mark_as_paid()`, `unmark_as_paid()` — InstallmentService
- `adjust()` — InstallmentService
- `transition_status()` — ContractService, ItemService

## Consequências
- **Positivas**:
  - Cross-tenant access silencioso é impossível em qualquer método de serviço
  - Código mais explícito e defensivo
  - Helper centralizado permite mudar o comportamento (ex: código do erro) em um único lugar
- **Negativas**:
  - O parâmetro `company` em métodos como `delete()` agora serve apenas para logging + validação, não mais para lookup
  - Leve overhead de CPU por chamada (comparação de dois integers)
- **Neutras**:
  - Testes cross-tenant adicionados para todos os métodos validados

## Arquivos Afetados
- `backend/apps/core/tenant.py` (novo) — helper
- `backend/apps/*/services/*.py` (23 métodos em 10 services)
- `backend/apps/*/tests/*/test_services.py` (17 testes cross-tenant)
