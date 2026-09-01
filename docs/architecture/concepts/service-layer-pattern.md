---
title: "Padrão Service Layer & Orquestração de Domínio"
domain: architecture
type: concept
source_code:
  - backend/apps/core/models.py
  - backend/apps/finances/services/expense_service.py
  - backend/apps/finances/services/installment_service.py
tests:
  - backend/apps/finances/tests/expenses/test_services.py
  - backend/apps/core/tests/test_atomic_service_audit.py
---

# Padrão Service Layer & Orquestração de Domínio

> **Categoria:** Conceito Arquitetural
> **Relacionados:** [ADR-006: Service Layer](../adr/006-service-layer.md) · [ADR-011: BaseModel save() com full_clean()](../adr/011-basemodel-save-full-clean.md) · [Padrão Query Selectors](query-selectors-pattern.md) · [Estratégia de Multi-Tenancy](multi-tenancy-strategy.md) · [Atomic Service Audit Guard](../../reference/architecture-standards/guard-rails/atomic-service-audit-guard.md)

---

## 1. Visão Geral e Racional Arquitetural

A **Service Layer** é o núcleo de processamento de regras de negócio, validação de invariantes e orquestração de efeitos colaterais no backend.

O framework web (**Django Ninja**) atua estritamente como um adaptador de transporte HTTP (camada de entrada). Os controladores em `api.py` não contêm lógica de negócio, consultas ORM diretas nem regras de domínio; eles apenas deserializam schemas de entrada, injetam o contexto autenticado (`request.user.company`) e delegam a mutação para os métodos de serviço em `services/`.

---

## 2. Diagrama de Sequência Fullstack (Comando de Mutação)

```mermaid
sequenceDiagram
    autonumber
    actor User as Planejador / Noivos
    participant UI as Frontend React 19 (Smart Form)
    participant API as Django Ninja Router (api/expenses.py)
    participant Service as ExpenseService (services/expense_service.py)
    participant Shortcut as resolve_tenant_resource (shortcuts.py)
    participant Model as Domain Model Expense (models/expense.py)
    participant SubService as InstallmentService (services/installment_service.py)
    participant DB as PostgreSQL (Neon DB)

    User->>UI: Submete formulário de Despesa com Parcelamento
    UI->>API: POST /api/v1/finances/expenses/ (Payload JSON + Bearer JWT)
    Note over API: Injeta company de AuthRequest e chama ExpenseService.create
    API->>Service: ExpenseService.create(company, payload)
    Note over Service: Inicia transação atômica (@transaction.atomic)
    Service->>Shortcut: Resolve BudgetCategory e valida tenant
    Shortcut-->>Service: Instância category validada
    Service->>Service: Valida integridade cross-wedding & regra BR-F02
    Service->>Model: Instancia Expense(company, category, ...)
    Service->>Model: expense.save()
    Note over Model: BaseModel.save() executa self.full_clean() antes de persistir
    Model->>DB: INSERT INTO expenses (...)
    DB-->>Model: Retorna ID gerado
    Service->>SubService: InstallmentService.auto_generate_installments(...)
    Note over SubService: Calcula parcelas centesimais e persiste cada uma
    SubService->>DB: INSERT INTO installments (...)
    DB-->>SubService: Confirmação de persistência
    Note over Service: Commit automático da transação @transaction.atomic
    Service-->>API: Instância Expense criada
    API-->>UI: HTTP 201 Created (ExpenseOut Schema DTO)
    UI-->>User: Feedback visual de sucesso via Toast (Sonner)
```

---

## 3. Diretrizes e Invariantes da Service Layer

### A. CQRS-lite: Separação Estrita de Leitura e Escrita
- **`selectors/` (Queries / Leitura):** Funções puras dedicadas exclusivamente a buscar e projetar dados. Retornam instâncias de modelos ou `TenantQuerySet` encadeáveis e *lazy*. Não realizam `save()`, `delete()` nem alteram estado do banco.
- **`services/` (Commands / Mutações):** Classes ou funções com responsabilidade exclusiva sobre escrita (`create`, `update`, `delete`, `transition`), validação cruzada entre agregados, bloqueios concorrentes (`select_for_update`) e disparo de eventos.

### B. Transações Atômicas Obrigatórias (`@transaction.atomic`)
Qualquer mutação que envolva múltiplas tabelas ou múltiplos registros ORM deve ser decorada com `@transaction.atomic`. Em caso de exceção de validação ou erro de banco em qualquer ponto do fluxo, a transação é revertida integralmente (*rollback*), impedindo estados inconsistentes.

### C. Validação de Invariantes via `full_clean()` no `save()`
Conforme estabelecido na [ADR-011](../adr/011-basemodel-save-full-clean.md), todos os modelos herdando de `BaseModel` executam `self.full_clean()` dentro de `save()`, prevenindo que chamadas no nível de serviço contornem os validadores dos campos ou do método `clean()`.

```python
--8<-- "backend/apps/core/models.py:20:31"
```

---

## 4. Implementação Real: `ExpenseService.create`

O trecho a seguir demonstra a orquestração completa de criação de despesas, validação com contrato (BR-F02), transação atômica e geração automática de parcelas financeiras:

```python
--8<-- "backend/apps/finances/services/expense_service.py:93:196"
```

---

## 5. Tratamento Padronizado de Exceções de Domínio

A Service Layer não retorna códigos HTTP ou respostas customizadas; ela lança exceções de domínio tipadas:

| Exceção de Domínio | Significado | Status HTTP Envelopeado |
| :--- | :--- | :--- |
| **`ObjectNotFoundError`** | Recurso inexistente ou pertencente a outro tenant (IDOR) | `404 Not Found` |
| **`BusinessRuleViolation`** | Violação de regra de negócio funcional (ex: BR-F02, saldo inválido) | `400 Bad Request` |
| **`DomainIntegrityError`** | Inconsistência de integridade relacional entre agregados | `422 Unprocessable Entity` |
| **`PermissionDeniedError`** | Usuário sem nível de acesso para a operação | `403 Forbidden` |

Essas exceções são capturadas pelos *Exception Handlers* globais registrados na instância do Django Ninja (`config/api.py`), garantindo que o frontend receba sempre o envelope padronizado de erro (`error_code`, `message`, `details`).

---

## 6. Auditoria Estática e Testes Automatizados

A conformidade da Service Layer é auditada continuamente:
1. **Auditoria AST de Transações (`test_atomic_service_audit.py`):** Analisa a árvore sintática (AST) do Python para verificar se todos os métodos de escrita em `services/` possuem `@transaction.atomic` ou `with transaction.atomic():`.
2. **Testes Unitários de Domínio (`apps/finances/tests/expenses/test_services.py`):** Cobrem 100% dos caminhos de sucesso e cenários de exceção esperados.
