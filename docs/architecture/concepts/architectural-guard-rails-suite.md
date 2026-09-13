---
title: "Suíte de Guard-Rails Arquiteturais e Integridade Estática"
domain: architecture
type: concept
source_code:
  - backend/apps/core/tests/test_api_architecture.py
  - backend/apps/core/tests/test_atomic_service_audit.py
  - backend/apps/core/tests/test_tenant_isolation.py
  - backend/apps/core/tests/test_sensitive_data_leak.py
tests:
  - backend/apps/core/tests/
---

# Suíte de Guard-Rails Arquiteturais e Integridade Estática

> **Categoria:** Conceito Arquitetural
> **Relacionados:** [Índice de Guard-Rails](../../reference/architecture-standards/guard-rails/index.md) · [Tenant Isolation Guard](../../reference/architecture-standards/guard-rails/tenant-isolation-guard.md) · [Atomic Service Audit Guard](../../reference/architecture-standards/guard-rails/atomic-service-audit-guard.md) · [Security Permissions Guard](../../reference/architecture-standards/guard-rails/security-permissions-guard.md) · [Pipeline de CI/CD](ci-cd-pipeline-flow.md) · [ADR-029: Modern Task Runner (Just)](../adr/029-modern-task-runner-just.md) · [Visão Geral do Sistema](system-overview.md)

---

## 1. Visão Geral e Filosofia dos Guard-Rails

A suíte localizada em `backend/apps/core/tests/` atua como a **barreira de integridade dinâmica e estática** do sistema.

Em vez de testar regras de negócio específicas de um domínio isolado, esses testes realizam **metaprogramação e análise de Árvore Sintática Abstrata (AST)** sobre toda a base de código (`backend/apps/`), convertendo as Decisões Arquiteturais (ADRs) em asserções executáveis pelo `pytest`.

### Por que Guard-Rails Automatizados?
1. **Prevenção de Erosão Arquitetural (*Architecture Drift*):** Impede que novas implementações quebrem convenções de projeto (ex: esquecer `operation_id` em um endpoint ou realizar escrita fora de transação).
2. **Auditoria de Segurança Contínua:** Bloqueia automaticamente vazamentos de PII, senhas ou quebras de isolamento multitenant antes do merge em staging ou produção.
3. **Feedback Imediato no Developer Loop:** Executados em menos de 3 segundos no comando local `just check-ci` (ou `just test` / `uv run poe test`).

---

## 2. Diagrama do Pipeline de Auditoria de Guard-Rails

```mermaid
flowchart TD
    subgraph INPUT["1. Entrada do Código-Fonte"]
        CODE["backend/apps/**"]
        ROUTERS["config.api.api (Django Ninja Instance)"]
    end

    subgraph AUDITORS["2. Motores de Auditoria Automatizada (pytest apps/core/tests/)"]
        direction TB
        AST_ENGINE["Análise Estática de AST Python<br/>(test_atomic_service_audit.py)"]
        RUNTIME_ENGINE["Inspeção de Rotas & Schemas em Runtime<br/>(test_api_architecture.py)"]
        SECURITY_ENGINE["Varredura de PII & Segurança<br/>(test_sensitive_data_leak.py)"]
        TENANT_ENGINE["Auditoria de Modelos & QuerySets<br/>(test_tenant_isolation.py)"]
    end

    subgraph GATES["3. Barreira de Qualidade (Quality Gate)"]
        PASS["Build Aprovado (CI Green)"]
        FAIL["Build Rejeitado com Código de Violação"]
    end

    CODE --> AST_ENGINE
    ROUTERS --> RUNTIME_ENGINE
    CODE --> SECURITY_ENGINE
    CODE --> TENANT_ENGINE

    AST_ENGINE -->|Valida @transaction.atomic| GATES
    RUNTIME_ENGINE -->|Valida operation_id & 401 shields| GATES
    SECURITY_ENGINE -->|Bloqueia passwords em outputs| GATES
    TENANT_ENGINE -->|Força for_tenant em todos os modelos| GATES
```

---

## 3. Catálogo dos Principais Guard-Rails

### A. Auditoria de Operation IDs da API Ninja (`test_api_architecture.py`)
Inspeciona todos os roteadores registrados na instância global do Django Ninja e assegura que 100% dos endpoints possuam um `operation_id` explícito e não vazio. Essa regra é crítica para a geração determinística dos hooks TypeScript no frontend via Orval:

```python
--8<-- "backend/apps/core/tests/test_api_architecture.py:26:51"
```

### B. Auditoria Estática de Transações Atômicas via AST (`test_atomic_service_audit.py`)
Varre a árvore sintática (AST) de todos os arquivos em `apps/*/services/` e detecta métodos que invocam mutações no ORM (`save`, `create`, `update`, `delete`, `bulk_*`). Caso a função não esteja decorada com `@transaction.atomic` ou encapsulada em `with transaction.atomic():`, o teste falha:

```python
--8<-- "backend/apps/core/tests/test_atomic_service_audit.py:45:54"
```

### C. Isolamento Multitenant (`test_tenant_isolation.py`)
- Valida que todos os modelos de domínio herdam de `TenantModel`.
- Audita se os Managers padrão são instâncias de `TenantManager`.
- Testa cenários de cruzamento de tenants para garantir que nenhum dado vaze entre contas.

### D. Blindagem Contra Vazamento de Dados Sensíveis (`test_sensitive_data_leak.py`)
- Inspeciona os Schemas de saída do Django Ninja para assegurar que campos como `password`, `token`, `secret_key` ou `hash` nunca sejam serializados para o cliente.

---

## 4. Execução e Integração Contínua (CI/CD)

Os guard-rails arquiteturais rodam em dois momentos obrigatórios:
1. **Localmente:** `pytest backend/apps/core/tests/` ou como parte de `just check-ci` (ou `just test` / `uv run poe test`).
2. **GitHub Actions:** No workflow `.github/workflows/ci-pr-validation.yml` em todo Pull Request aberto para `develop` ou `main`.
