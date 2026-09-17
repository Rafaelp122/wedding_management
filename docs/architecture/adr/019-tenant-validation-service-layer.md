# ADR-019: Validação de Tenant na Camada de Serviço

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟡 Consolidada na [ADR-016: Multi-tenancy Pragmático](016-pragmatic-multi-tenancy.md)
> **Data:** Fevereiro 2026
> **Decisor:** Rafael
> **Relacionados:** [ADR-016: Multi-tenancy Pragmático](016-pragmatic-multi-tenancy.md) · [Guard-Rail de Isolação Multitenant](../../reference/architecture-standards/guard-rails/tenant-isolation-guard.md)

> [!NOTE]
> **Consolidação Arquitetural (Fevereiro 2026):**
> O helper defensivo `validate_tenant_ownership()` introduzido nesta ADR foi consolidado e incorporado como o **Pilar 4** da arquitetura corporativa oficial definida na [ADR-016: Multi-tenancy Pragmático](016-pragmatic-multi-tenancy.md).

---

## 1. Contexto e Problema

A arquitetura de multi-tenancy do sistema isola os dados verticalmente por `Company` através do `TenantManager` com `.for_tenant(company)` nas consultas ao banco de dados. No entanto, diversos métodos da camada de serviço (`update()`, `delete()`, `mark_as_paid()`, etc.) recebem uma instância do modelo já carregada — seja pela API (que faz `get()` antes de chamar o service) ou por chamadas internas entre services.

Nesses métodos, o parâmetro `company` era recebido mas nunca validado contra a instância. Embora chamadas diretas da API estivessem protegidas pelo filtro no lookup inicial, chamadas internas entre serviços ou falhas na camada de apresentação poderiam operar inadvertidamente sobre dados de outra empresa.

---

## 2. Decisão

Criar um helper centralizado e defensivo `validate_tenant_ownership(company, instance, ...)` que verifica se `instance.company_id == company.id`, levantando `ObjectNotFoundError` (HTTP 404) em caso de divergência.

### Racional da Resposta HTTP 404 vs 403
Retornar HTTP 403 (*Forbidden*) revelaria a um atacante que o recurso de fato existe em outro tenant (ataque de enumeração IDOR). Retornar HTTP 404 torna os cenários "recurso inexistente" e "recurso pertencente a outra empresa" completamente indistinguíveis para o cliente externo, seguindo a boa prática de segurança em SaaS multi-tenant.

```python
def validate_tenant_ownership(company, instance, *, detail: str, code: str) -> None:
    """Garante que a entidade manipulada pertence estritamente ao tenant ativo."""
    if instance.company_id != company.id:
        raise ObjectNotFoundError(detail=detail, code=code)
```

---

## 3. Consequências

### Positivas :material-check-circle:
- **Proteção Contra IDOR:** Impossibilita acesso silencioso entre empresas em qualquer método de mutação na camada de serviço.
- **Defesa em Profundidade:** Mesmo em invocações internas entre serviços onde uma instância pré-carregada é repassada, o pertencimento corporativo é verificado.
- **Centralização:** Comportamento de auditoria e exceção padronizado em um único ponto.

### Negativas / Trade-offs :material-close-circle:
- **Parâmetro Mandatório:** Todo método de mutação deve exigir explicitamente `company` como primeiro argumento posicional.
- **Sobrecarga Mínima:** Comparação trivial de inteiros (`instance.company_id != company.id`) em memória.

---

## 4. Referências

- [ADR-016: Multi-tenancy Pragmático e Orientado a Organização](016-pragmatic-multi-tenancy.md)
- [Guard-Rail de Isolação Multitenant](../../reference/architecture-standards/guard-rails/tenant-isolation-guard.md)
