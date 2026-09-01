---
title: "Distribuição e Alocação de Orçamento por Categoria"
domain: finances
type: business-rule
source_code:
  - backend/apps/finances/services/budget_category_service.py
  - backend/apps/finances/services/budget_service.py
  - backend/apps/finances/models/budget.py
  - backend/apps/finances/models/budget_category.py
tests:
  - backend/apps/finances/tests/categories/test_services.py
  - backend/apps/finances/tests/budgets/test_services.py
---

# Distribuição e Alocação de Orçamento por Categoria

> **Categoria:** Regra de Negócio (Domínio Financeiro)
> **Relacionados:** [Regras de Integridade Financeira](financial-integrity-rules.md) · [Lógica de Parcelas Vencidas](installment-overdue-logic.md) · [Domínio de Finanças](../../domains/finances-domain.md)

---

## 1. Contexto e Invariantes do Domínio

A gestão orçamentária do casamento é estruturada em torno de um **Teto Financeiro Mestre** (`Budget.total_estimated`) e de **Categorias Orçamentárias** (`BudgetCategory.allocated_budget`). A alocação por categoria serve como balizador para que o assessor e o casal monitorem o comprometimento financeiro por segmento (ex.: Buffet, Decoração, Foto & Vídeo).

### Invariantes Fundamentais:
1. **Conservação do Teto Orçamentário (Budget Cap Guard):** A soma dos valores alocados em todas as categorias de um casamento não pode ultrapassar o teto global estimado do orçamento mestre.
2. **Proteção contra Condições de Corrida (TOCTOU):** Mutações de alocação de categoria (`create` e `update`) realizam lock pessimista do registro de orçamento pai via `select_for_update()` antes da soma agregada, prevenindo ultrapassagem de teto por requisições concorrentes.
3. **Idempotência de Categorias Padrão:** Na criação sob demanda do orçamento mestre, são geradas 6 categorias iniciais canônicas com `allocated_budget = Decimal('0.00')`.
4. **Proteção de Exclusão de Categoria (`category_protected_error`):** Uma categoria não pode ser excluída do banco de dados caso possua despesas ativas associadas (`instance.expenses.exists()`).

### Fórmulas Matemáticas de Alocação:
Para um casamento com orçamento mestre $T_{\text{estimated}}$ e $M$ categorias orçamentárias onde cada categoria $k$ possui uma verba alocada $A_k$:

$$\sum_{k=1}^{M} A_k \le T_{\text{estimated}}$$

Na atualização ou criação da categoria $i$ com nova alocação $A_i$, a validação calcula:

$$A_{\text{irmãos}} = \sum_{k \ne i} A_k$$

$$\text{Margem Disponível} = T_{\text{estimated}} - A_{\text{irmãos}}$$

$$\text{Se } (A_{\text{irmãos}} + A_i) > T_{\text{estimated}} \implies \text{Raise } \text{BusinessRuleViolation}(\text{'budget\_cap\_exceeded'})$$

---

## 2. Diagrama de Fluxo e Validação com Lock Pessimista

```mermaid
graph TD
    A["Início: BudgetCategoryService.create / update"] --> B["1. Validar Tenant & Ownership (ADR-009)"]
    B --> C["2. Obter lock no Orçamento Mestre:<br/>Budget.objects.for_tenant(company).select_for_update().get(pk=budget.pk)"]
    C --> D["3. Executar full_clean() da Categoria"]
    D --> E["4. Agregar soma dos irmãos:<br/>BudgetCategory.objects.exclude(pk).aggregate(Sum('allocated_budget'))"]
    E --> F{"Soma Irmãos + Categoria Atual > budget.total_estimated?"}

    F -->|Sim| ERR["Raise BusinessRuleViolation<br/>('budget_cap_exceeded')"]
    F -->|Não| G["5. Persistir Categoria (save)"]
    G --> H["Fim: Categoria Criada / Atualizada com Sucesso"]
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Ação do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-F04-A** | **Teto de Alocação** | `allocated_siblings + category.allocated_budget > budget.total_estimated` | `BusinessRuleViolation` (`budget_cap_exceeded`) | Bloqueia a criação/edição e impede sobrealocação do orçamento mestre. |
| **BR-F04-B** | **Lock Anti-TOCTOU** | Chamada concorrente a `create` ou `update` de categoria. | Protegido por `select_for_update()` | Serializa as validações e leituras de soma no banco de dados. |
| **BR-F04-C** | **Categorias Padrão Canônicas** | Execução de `BudgetCategoryService.setup_defaults()`. | Nenhuma (Idempotente) | Cria 6 categorias essenciais se não existirem (alocação inicial R$ 0,00). |
| **BR-F04-D** | **Proteção de Despesas Ativas** | Tentativa de deletar categoria que possui despesas (`expenses.exists()`). | `DomainIntegrityError` (`category_protected_error`) | Impede deleção física para evitar despesas órfãs ou sem categorização. |

---

## 4. Implementação no Código-Fonte Real

### A. Validação de Teto com Agregação Segura (`budget_category_service.py`)

```python
--8<-- "backend/apps/finances/services/budget_category_service.py:22:53"
```

### B. Criação com Lock Pessimista (`budget_category_service.py`)

```python
--8<-- "backend/apps/finances/services/budget_category_service.py:63:113"
```

### C. Geração Idempotente de Categorias Canônicas (`budget_category_service.py`)

```python
--8<-- "backend/apps/finances/services/budget_category_service.py:213:261"
```

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes unitários em `apps/finances/tests/categories/test_services.py` e `apps/finances/tests/budgets/test_services.py` valida 100% dos fluxos de distribuição:

- `test_create_category_exceeds_budget_cap_raises_error`: Valida a rejeição ao ultrapassar o teto na criação.
- `test_create_category_uses_select_for_update`: Valida o uso de `select_for_update()` para prevenção de race conditions.
- `test_update_category_allocated_budget_exceeds_cap_raises_error`: Valida a rejeição ao extrapolar o teto em atualizações parciais.
- `test_delete_category_with_expenses_fails`: Valida o bloqueio de exclusão quando há despesas associadas.
- `test_setup_defaults_creates_six_categories`: Valida criação das 6 categorias canônicas padrão.
- `test_setup_defaults_is_idempotent`: Valida que chamadas subsequentes de setup não duplicam categorias.
