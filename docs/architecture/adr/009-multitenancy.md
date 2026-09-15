# ADR-009: Multitenancy Denormalizado

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟡 Superada e Integrada pela [ADR-016: Multi-tenancy Pragmático](016-pragmatic-multi-tenancy.md)
> **Data:** Janeiro 2025
> **Decisor:** Rafael
> **Relacionados:** [ADR-016: Multi-tenancy Pragmático](016-pragmatic-multi-tenancy.md) · [ADR-019: Validação de Tenant na Camada de Serviço](019-tenant-validation-service-layer.md)

> [!WARNING]
> **Decisão Histórica / Superada pela [ADR-016: Multi-tenancy Pragmático](016-pragmatic-multi-tenancy.md)**:
> A estratégia original baseada em casamentos individuais como unidade primária de isolamento multi-tenant (`WeddingOwnedMixin`) foi substituída e consolidada pelo isolamento organizacional corporativo (`Company` / `TenantModel`) definido na [ADR-016](016-pragmatic-multi-tenancy.md). O isolamento por casamento permanece no domínio apenas como filtro secundário de agrupamento dentro do escopo de cada empresa contratante.

---

## 1. Contexto e Problema

Nos estágios iniciais do projeto, precisávamos isolar os dados entre diferentes casamentos (weddings) para garantir confidencialidade e alta velocidade de consulta:

1. **Garantia de Isolamento:** Usuários de um casamento não podem visualizar despesas, contratos ou cronogramas de outro.
2. **Eficiência de Consulta:** Consultas de agregação e listagens de despesas exigiam filtros rápidos sem sobrecarga excessiva de junções relacionais.
3. **Prevenção de Referências Cruzadas:** Bloqueio de cadastros cruzados onde itens de um casamento pudessem ser vinculados a outro.

### Alternativas Consideradas

1. **Schema-based (1 Schema PostgreSQL por Tenant):** Alto isolamento físico, porém inviável para escalabilidade em banco serverless devido ao overhead operacional de migrations.
2. **Database-based (1 Banco por Tenant):** Complexidade e custo desproporcionais para o estágio do projeto.
3. **Row-based Normalizado (Isolamento via Cadeia de Relacionamentos):** Requer 3 a 4 `JOINs` relacionais em cada consulta de despesa (`wedding -> category -> item -> expense`), degradando a performance.
4. **Row-based Denormalizado (Escolhido Originalmente):** Inclusão de chave de pertencimento direta em todas as tabelas filhas.

---

## 2. Decisão

Adotar inicialmente o modelo **Row-based Denormalizado**:
- Inclusão direta de chave de pertencimento nos modelos agregados.
- Filtragem mandante em todas as consultas do ORM.
- Validação defensiva de consistência referencial no método `clean()` dos modelos.

### Comparativo de Abordagens

| Aspecto | Denormalizado (Escolha Original) | Normalizado (Cadeia de 4 JOINs) | Schema-based | Tenant Corporativo ([ADR-016](016-pragmatic-multi-tenancy.md) - Vigente) |
| :--- | :--- | :--- | :--- | :--- |
| **Performance** | :material-check-circle: Consulta direta indexada | :material-close-circle: Junções custosas | :material-check-circle: Isolamento por schema | :material-check-circle: Index Scan por `(company, uuid)` |
| **Simplicidade** | :material-check-circle: Simples no ORM | :material-alert: Complexidade em queries | :material-close-circle: Complexidade em migrations | :material-check-circle: `TenantModel` e `TenantManager` |
| **Escalabilidade SaaS** | :material-alert: Limitado a 1 usuário por wedding | :material-alert: Inviável para relatórios amplos | :material-close-circle: Limite físico de conexões/schemas | :material-check-circle: Organizações com múltiplos assessores |
| **Governança** | :material-close-circle: Sem agrupamento por empresa | :material-close-circle: Sem agrupamento corporativo | :material-alert: Alto custo de infraestrutura | :material-check-circle: Gestão corporativa, planos e cotas |

---

## 3. Consequências

### Positivas :material-check-circle:
- **Performance de Leitura:** Consultas com filtro direto em chave indexada eliminando junções profundas no PostgreSQL.
- **Simplicidade de Filtros:** Filtragem uniforme em selectors e managers sem dependência de cadeias relacionais complexas.
- **Defesa em Profundidade:** Validações de integridade entre chaves estrangeiras executadas em `clean()`.

### Negativas / Trade-offs :material-close-circle:
- **Limitação de Modelo de Negócio:** Modelar o casamento como tenant direto impedia colaboração entre múltiplos assessores da mesma agência — limitação superada pela arquitetura corporativa da [ADR-016](016-pragmatic-multi-tenancy.md).
- **Sobrecarga de Denormalização:** Duplicação de chaves de vínculo em todas as tabelas filhas e necessidade de validações explícitas de consistência.

---

## 4. Referências

- [ADR-016: Multi-tenancy Pragmático e Orientado a Organização](016-pragmatic-multi-tenancy.md)
- [ADR-019: Validação de Tenant na Camada de Serviço](019-tenant-validation-service-layer.md)
- [Guard-Rail de Isolação Multitenant](../../reference/architecture-standards/guard-rails/tenant-isolation-guard.md)
