---
title: "Hierarquia Pai-Filho e Termos Aditivos de Contratos"
domain: logistics
type: business-rule
source_code:
  - backend/apps/contracts/models/contract.py
  - backend/apps/contracts/services/contract_service.py
  - backend/apps/contracts/selectors/contract_selectors.py
tests:
  - backend/apps/contracts/tests/test_models.py
  - backend/apps/contracts/tests/test_services.py
  - backend/apps/contracts/tests/test_selectors.py
---

# Hierarquia de Contratos e Termos Aditivos

> **Categoria:** Regra de Negócio (Domínio Logístico)
> **Relacionados:** [Catálogo de Regras](../index.md) · [Máquina de Estados de Contratos](contract-state-machine.md) · [Validação de CNPJ](cnpj-validation-rules.md) · [Regras de Integridade Financeira](../finances/financial-integrity-rules.md) · [Domínio de Logística](../../domains/logistics-domain.md)

---

## 1. Contexto e Invariantes do Domínio

No ciclo de contratações de um casamento, alterações de escopo, reajustes de valores e contratações complementares de um mesmo fornecedor são formalizadas como **Termos Aditivos**. No modelo de dados, aditivos são entidade filha dedicada (`ContractAddendum`) vinculada ao contrato principal por relação 1:N estrita (`contract = ForeignKey(Contract, on_delete=CASCADE, related_name="addendums")`). O auto-relacionamento recursivo (`parent = ForeignKey("self")`) foi removido na Onda 3 da RFC-001 (`logistics/0012`, `contracts/0002`).

### Invariantes Fundamentais e Travas de Integridade:
1. **Alinhamento de Contrato ($A.\text{contract\_id} == C.\text{id}$):** Todo aditivo pertence a exatamente um contrato — validado no modelo (`ContractAddendum._clean_contract_alignment`, herdando `wedding`/`company` do contrato quando vazios) e no serviço (`ContractAddendumService.sign/cancel/delete` disparam `addendum_contract_mismatch`).
2. **Bloqueio Cross-Wedding ($A.\text{wedding\_id} == C.\text{wedding\_id}$):** O aditivo deve pertencer obrigatoriamente ao mesmo casamento do contrato principal.
3. **Sem Grafo (Relação Plana 1:N):** Por não existir auto-relacionamento, ciclos hierárquicos são impossíveis por construção — o Graph Cycle Guard legado foi removido com o campo `parent`.
4. **Deleção em Cascata e Proteções (`CASCADE` + `ProtectedError`):** A exclusão do contrato principal remove seus aditivos (`on_delete=CASCADE`). A exclusão do próprio contrato é bloqueada se `SIGNED` (`cannot_delete_signed_contract`) ou se houver despesas/itens vinculados (`ProtectedError` → `contract_has_protected_dependencies`). Aditivos `SIGNED` não podem ser excluídos (`cannot_delete_signed_addendum`).

### Fórmulas Matemáticas de Consolidação Financeira:
Para um contrato principal $C$ com valor de face $V_{\text{principal}}$ e um conjunto de termos aditivos $A \in \text{Addendums}(C)$, o **Valor Efetivo** soma exclusivamente aditivos formalmente assinados. Aditivos `PENDING` são expectativa futura (expostos separadamente em `addendums_pending_total`) e `CANCELED` nunca compõem:

$$V_{\text{efetivo}} = V_{\text{principal}} + \sum_{\substack{A \in \text{Addendums}(C) \\ \text{status}(A) = \text{SIGNED}}} V_A$$

O `ContractQuerySet.with_totals()` anota `addendums_total` (SIGNED), `addendums_pending_total` (PENDING) e `effective_amount` diretamente no banco de dados via `Subquery` (eliminando problemas de desempenho N+1), e a consulta pontual utiliza o `contract_consolidated_total_selector` (SIGNED-only).

---

## 2. Diagrama de Estrutura e Grafo de Validação

```mermaid
graph TD
    subgraph "Estrutura Válida (1:N plano)"
        CP["Contrato Principal (Buffet) <br/> Total: R$ 20.000,00"]
        AD1["Termo Aditivo 1 (Bebidas Extras) <br/> Total: R$ 3.000,00"]
        AD2["Termo Aditivo 2 (Hora Adicional) <br/> Total: R$ 1.500,00"]

        CP -->|contract FK| AD1
        CP -->|contract FK| AD2
    end

    subgraph "Travas de Integridade Bloqueadas"
        A["Aditivo X"] -.->|Bloqueio Alinhamento (contract_id divergente)| C["Contrato Y"]

        W1["Casamento 1 (Aditivo)"] -.->|Bloqueio Cross-Wedding| W2["Casamento 2 (Contrato)"]

        S["Contrato SIGNED"] -.->|Bloqueio Deleção| DEL["Exclusão Física"]
    end
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Ação do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-L02-A** | **Alinhamento Contrato-Aditivo** | `addendum.contract_id != contract.id` em sign/cancel/delete | `DomainIntegrityError` (`addendum_contract_mismatch`) | Impede operar aditivo sob contrato divergente. |
| **BR-L02-B** | **Guarda Cross-Wedding** | `addendum.wedding_id != contract.wedding_id` | `ValidationError` (modelo) | Impede contaminação de aditivos entre casamentos diferentes. |
| **BR-L02-C** | **Relação Plana 1:N (sem grafo)** | N/A por construção | N/A | Ciclos hierárquicos impossíveis após remoção do `parent` recursivo (Onda 3). |
| **BR-L02-D** | **Proteção de Deleção** | Deleção de contrato `SIGNED` ou com despesas/itens; deleção de aditivo `SIGNED` | `BusinessRuleViolation` (`cannot_delete_signed_contract` / `cannot_delete_signed_addendum`) / `BusinessRuleViolation` (`contract_has_protected_dependencies`) | Aditivos caem em cascata (`CASCADE`) com o contrato principal. |
| **BR-L02-E** | **Composição SIGNED-only** | Aditivo com `status != "SIGNED"` | Nenhuma (Tratamento Seletor) | Somente aditivos assinados compõem `effective_amount`; `PENDING` exposto em `addendums_pending_total`. |

---

## 4. Implementação no Código-Fonte Real

- **Validação no Modelo:** [`ContractAddendum._clean_contract_alignment()`](../../../../backend/apps/contracts/models/contract_addendum.py)
- **Guarda de Alinhamento no Serviço:** [`ContractAddendumService.sign/cancel/delete`](../../../../backend/apps/contracts/services/contract_addendum_service.py) (`addendum_contract_mismatch`)
- **Consulta de Totais Consolidados:** [`contract_consolidated_total_selector()`](../../../../backend/apps/contracts/selectors/contract_selectors.py) (SIGNED-only) e [`ContractQuerySet.with_totals()`](../../../../backend/apps/contracts/managers.py) (`addendums_total`, `addendums_pending_total`, `effective_amount`)

### A. Alinhamento de Contrato e Wedding no Modelo (`contract_addendum.py`)

```python
def _clean_contract_alignment(self) -> None:
    # Herda wedding/company do contrato quando vazios; senão valida igualdade
    # (addendum.wedding_id == contract.wedding_id, mesmo company_id).
```

### B. Guarda de Alinhamento no Serviço (`contract_addendum_service.py`)

```python
if addendum.contract_id != contract.id:
    raise DomainIntegrityError(
        detail="O termo aditivo informado não pertence ao contrato especificado.",
        code="addendum_contract_mismatch",
    )
```

### C. Seletor de Valor Efetivo (`contract_selectors.py`)

```python
def contract_consolidated_total_selector(company: Company, contract: Contract) -> Decimal:
    validate_tenant_ownership(company, contract, ...)
    addendums_sum = (
        contract.addendums.for_tenant(company)
        .filter(status=ContractAddendum.StatusChoices.SIGNED)
        .aggregate(total=Sum("amount"))["total"]
    )
    return (contract.total_amount or Decimal("0.00")) + (addendums_sum or Decimal("0.00"))
```

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes unitários em `apps/contracts/tests/test_models.py`, `apps/contracts/tests/test_services.py` e `apps/contracts/tests/test_selectors.py` garante cobertura das regras de aditivos:

- `test_contract_consolidated_total_selector`: Valida a soma SIGNED-only (face + assinados; PENDING e CANCELED fora).
- `test_with_totals_annotates_pending_addendums`: Valida `addendums_total` vs `addendums_pending_total` separados.
- `test_with_totals_scopes_subqueries_by_tenant`: Valida isolamento de tenant nas agregações.
- Testes de `sign/cancel/delete` de aditivos com `addendum_contract_mismatch` e travas de SIGNED.
