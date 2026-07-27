# MOC de Domínio: Core & Infraestrutura

> **Hub de Domínio:** [core-domain](core-domain.md) | [system-overview](../architecture/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/core/` & `frontend/src/lib/`, `src/components/ui/`

---

## Visão Geral do Módulo Core

O módulo **Core** fornece a fundação transversal de infraestrutura, utilitários, base models, exceções globais, utilitários de tenant e a suíte de testes de guard-rails de segurança e arquitetura.

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/core/`)
- **Base Models & Mixins:**
  - `BaseModel`: Validação automática `full_clean()` no `save()` (ADR-011). Veja [core-models](../../3-reference/models/core-models.md).
  - `SoftDeleteModel`: Padrão de exclusão lógica (ADR-008). Veja [core-models](../../3-reference/models/core-models.md).
  - `WeddingOwnedMixin`: Injeção de pertencimento a casamento. Veja [core-models](../../3-reference/models/core-models.md).
- **Exception Handler:** Envelope padronizado de erro HTTP (ADR-010). Veja [error-envelope-spec](../../3-reference/api/error-envelope-spec.md).
- **Suíte de Testes de Guard-Rails Arquiteturais (`backend/apps/core/tests/`):**
  - Testes automatizados de auditoria para 12 pilares do sistema (Isolação Multitenant, Proteção contra Cascade Delete, Transações Atômicas, `operation_id`, Envelopes de Erro, Prevenção de Vazamentos de Dados, Concorrência, Performance N+1 e Segurança). Veja [architectural-guard-rails-suite](../architecture/architectural-guard-rails-suite.md).

### 2. Camada de Frontend (`frontend/src/`)
- **Componentes Base (shadcn/ui):** `Button`, `Dialog`, `Sheet`, `Table`, `Input`. Veja [ui-components-spec](../../3-reference/frontend/ui-components-spec.md).
- **Cliente HTTP Axios:** Interceptor de erros e JWT token injection em `src/api/client.ts`. Veja [auth-jwt-flow](../architecture/auth-jwt-flow.md).
- **Utilitários:** Funções de formatação de moeda (`formatCurrency`) e mesclagem de classes (`cn`).

---

## Links Atômicos Relacionados
- [architectural-guard-rails-suite](../architecture/architectural-guard-rails-suite.md)
- [core-models](../../3-reference/models/core-models.md)
- [error-envelope-spec](../../3-reference/api/error-envelope-spec.md)
- [ui-components-spec](../../3-reference/frontend/ui-components-spec.md)
- [multi-tenancy-strategy](../architecture/multi-tenancy-strategy.md)
