# Arquitetura: Padrão Query Selectors & Custom QuerySets

> **Módulo:** [query-selectors-pattern](query-selectors-pattern.md) | [service-layer-pattern](service-layer-pattern.md) | [system-overview](system-overview.md)
> **Referência Técnica:** [query-selectors-spec](../../3-reference/architecture-standards/query-selectors-spec.md)

---

## Visão Geral

O backend adota o padrão **Query Selectors** combinado com **Custom QuerySets (Managers)** para estabelecer uma separação formal entre operações de **Consulta (Queries)** e operações de **Modificação/Comando (Commands/Mutations)** — aplicando princípios de CQRS-lite (*Command-Query Responsibility Segregation*).

Nessa arquitetura:
- **`selectors/` (Leitura):** Funções puras que montam e executam consultas de leitura, isoladas por tenant e otimizadas com anotações e *pre-fetchings*.
- **`services/` (Escrita):** Classes e métodos dedicados exclusivamente a regras de negócio de mutação (`create`, `update`, `delete`), validação de invariantes de domínio e transações atômicas (`@transaction.atomic`).
- **`managers.py` (Custom QuerySets):** Blocos de construção granulares e reutilizáveis do ORM Django com métodos encadeáveis e avaliação *lazy*.

---

## Fluxo Arquitetural

```text
┌─────────────────────────────────────────────────────────┐
│                      Django Ninja                       │
│                        (api.py)                         │
└────────────┬───────────────────────────────┬────────────┘
             │ Consultas (GET)               │ Mutações (POST/PUT/PATCH/DELETE)
             ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│       selectors/         │    │        services/         │
│  (Consultas de Domínio)  │    │ (Mutações & Regras Excl) │
└────────────┬─────────────┘    └────────────┬─────────────┘
             │                               │
             └───────────────┬───────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│              managers.py / Custom QuerySet              │
│          (Filtros e anotações reaproveitáveis)          │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL / Domain Models                 │
└─────────────────────────────────────────────────────────┘
```

---

## Princípios Fundamentais

### 1. Encadeamento Fluente e Avaliação Preguiçosa (*Lazy Evaluation*)
As funções de listagem nos seletores (`*_list_selector`) retornam a instância do `CustomQuerySet` especializado (ex: `BudgetQuerySet`, `WeddingQuerySet`), e não listas Python materializadas em memória.

Isso preserva as principais vantagens do Django ORM:
- **Paginação Transparente:** O decorador `@paginate` do Django Ninja intercepta o `QuerySet` e aplica `LIMIT` e `OFFSET` diretamente no SQL executado no banco.
- **Componibilidade:** Endpoints ou seletores agregadores podem encadear novos filtros (`.filter(...)`, `.order_by(...)`) sobre a consulta base sem disparar queries intermediárias.

### 2. Multi-Tenancy Nativo e Obrigatório
Toda consulta inicia pelo escopo da empresa (`company: Company`) através do método `Model.objects.for_tenant(company)` herdado de `TenantQuerySet`. Isso impede qualquer vazamento de dados entre empresas (*cross-tenant data leakage*).

### 3. Serviços Limpos e Orientados a Ação
Os serviços deixam de ser classes "inchadas" com dezenas de métodos estáticos de busca e passam a se concentrar em:
- Validação de invariantes de domínio e regras de negócio complexas.
- Validação intrínseca via `full_clean()`.
- Gestão de transações e bloqueios concorrentes (`select_for_update`).
- Disparo de eventos e tarefas em segundo plano.

---

## Comparativo de Responsabilidades

| Responsabilidade | Custom QuerySet (`managers.py`) | Selector (`selectors/`) | Service (`services/`) |
| :--- | :--- | :--- | :--- |
| **Anotações SQL complexas** (Subqueries, Coalesce, Sum) | ✅ Sim (`.with_totals()`) | ❌ Não (apenas consome) | ❌ Não |
| **Filtros de domínio reutilizáveis** (`.pending()`, `.due_soon()`) | ✅ Sim | ❌ Não (apenas consome) | ❌ Não |
| **Orquestração de consultas de tela** | ❌ Não | ✅ Sim (`*_list_selector`) | ❌ Não |
| **Resolução de instância com 404** | ❌ Não | ✅ Sim (`*_get_selector`) | ❌ Não |
| **Mutações no banco** (`save()`, `delete()`) | ❌ Proibido | ❌ Proibido | ✅ Sim |
| **Transações Atômicas** (`@transaction.atomic`) | ❌ Não | ❌ Não | ✅ Sim |
| **Lançamento de `BusinessRuleViolation`** | ❌ Não | ❌ Não | ✅ Sim |
