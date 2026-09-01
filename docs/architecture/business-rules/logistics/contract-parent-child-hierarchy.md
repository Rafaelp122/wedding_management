---
title: "Hierarquia Pai-Filho e Termos Aditivos de Contratos"
domain: logistics
type: business-rule
source_code:
  - backend/apps/logistics/models/contract.py
  - backend/apps/logistics/services/contract_service.py
  - backend/apps/logistics/selectors/contract_selectors.py
tests:
  - backend/apps/logistics/tests/contracts/test_models.py
  - backend/apps/logistics/tests/contracts/test_services.py
  - backend/apps/logistics/tests/test_selectors.py
---

# Hierarquia de Contratos e Termos Aditivos

> **Categoria:** Regra de Negócio (Domínio Logístico)
> **Relacionados:** [Máquina de Estados de Contratos](contract-state-machine.md) · [Regras de Integridade Financeira](../finances/financial-integrity-rules.md) · [Domínio de Logística](../../domains/logistics-domain.md)

---

## 1. Contexto e Invariantes do Domínio

No ciclo de contratações de um casamento, alterações de escopo, reajustes de valores e contratações complementares de um mesmo fornecedor são formalizadas como **Termos Aditivos**. No modelo de dados, aditivos são contratos filhos vinculados a um contrato principal por meio do campo `parent = ForeignKey("self", on_delete=models.PROTECT, related_name="addendums")`.

### Invariantes Fundamentais e Travas de Integridade:
1. **Bloqueio de Auto-vínculo ($C \ne \text{parent}(C)$):** Um contrato não pode ser pai de si mesmo — validado no modelo (`Contract.clean()`) e no serviço (`ContractService._resolve_parent`, disparando `contract_self_parent`).
2. **Bloqueio Cross-Wedding ($C.\text{wedding\_id} == \text{parent}(C).\text{wedding\_id}$):** O contrato pai deve pertencer obrigatoriamente ao mesmo casamento do aditivo (`contract_cross_wedding_parent`).
3. **Prevenção de Ciclos no Grafo (Graph Cycle Guard):** O sistema percorre a árvore de ancestrais para garantir que o contrato pai selecionado não seja um descendente do contrato atual (`contract_circular_parent`).
4. **Proteção na Exclusão (`ProtectedError`):** A exclusão física de um contrato principal que possua termos aditivos é bloqueada pelo banco de dados (`on_delete=models.PROTECT`). O serviço intercepta `ProtectedError` e dispara `DomainIntegrityError('contract_protected_by_addendums')`.

### Fórmulas Matemáticas de Consolidação Financeira:
Para um contrato principal $C$ com valor de face $V_{\text{principal}}$ e um conjunto de termos aditivos $A \in \text{Addendums}(C)$, o **Valor Total Consolidado** é calculado desconsiderando aditivos com status `CANCELED`:

$$V_{\text{consolidado}} = V_{\text{principal}} + \sum_{\substack{A \in \text{Addendums}(C) \\ \text{status}(A) \ne \text{CANCELED}}} V_A$$

O `ContractQuerySet.with_totals()` anota esse total diretamente no banco de dados via `Subquery` (eliminando problemas de desempenho N+1), e a consulta pontual utiliza o `contract_consolidated_total_selector`.

---

## 2. Diagrama de Estrutura e Grafo de Validação

```mermaid
graph TD
    subgraph "Estrutura Hierárquica Válida (DAG)"
        CP["Contrato Principal (Buffet) <br/> Total: R$ 20.000,00"]
        AD1["Termo Aditivo 1 (Bebidas Extras) <br/> Total: R$ 3.000,00"]
        AD2["Termo Aditivo 2 (Hora Adicional) <br/> Total: R$ 1.500,00"]

        CP -->|parent| AD1
        CP -->|parent| AD2
    end

    subgraph "Travas de Integridade Bloqueadas"
        C_SELF["Contrato A"] -.->|Bloqueio Auto-Vínculo| C_SELF

        W1["Casamento 1 (Contrato A)"] -.->|Bloqueio Cross-Wedding| W2["Casamento 2 (Contrato B)"]

        A1["Contrato 1"] --> A2["Contrato 2"] --> A3["Contrato 3"]
        A3 -.->|Bloqueio Circular (Graph Cycle Guard)| A1
    end
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Ação do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-L02-A** | **Anti Auto-Vínculo** | `parent_id == instance.pk` | `BusinessRuleViolation` (`contract_self_parent`) | Impede que o contrato aponte para si mesmo como aditivo. |
| **BR-L02-B** | **Guarda Cross-Wedding** | `parent.wedding_id != instance.wedding_id` | `BusinessRuleViolation` (`contract_cross_wedding_parent`) | Impede contaminação de aditivos entre casamentos diferentes. |
| **BR-L02-C** | **Prevenção Circular** | Contrato pai é descendente na árvore hierárquica. | `BusinessRuleViolation` (`contract_circular_parent`) | Bloqueia ciclos infinitos na árvore de contratos. |
| **BR-L02-D** | **Proteção de Deleção** | Deleção de contrato pai que possui aditivos ativos. | `DomainIntegrityError` (`contract_protected_by_addendums`) | Exige a remoção ou desvinculação prévia dos termos aditivos filhos. |
| **BR-L02-E** | **Exclusão de Cancelados** | Aditivo possui `status = "CANCELED"`. | Nenhuma (Tratamento Seletor) | Subtrai/desconsidera aditivos cancelados da soma consolidada. |

---

## 4. Implementação no Código-Fonte Real

### A. Validação de Hierarquia no Modelo (`contract.py`)

```python
--8<-- "backend/apps/logistics/models/contract.py:181:196"
```

### B. Resolução e Trava Circular no Serviço (`contract_service.py`)

```python
--8<-- "backend/apps/logistics/services/contract_service.py:333:385"
```

### C. Seletor de Valor Total Consolidado (`contract_selectors.py`)

```python
--8<-- "backend/apps/logistics/selectors/contract_selectors.py:95:130"
```

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes unitários em `apps/logistics/tests/contracts/test_models.py`, `apps/logistics/tests/contracts/test_services.py` e `apps/logistics/tests/test_selectors.py` garante 100% de cobertura das regras hierárquicas:

- `test_contract_self_parent_fails`: Valida rejeição quando contrato tenta ser pai de si mesmo no model.
- `test_update_parent_self_raises_error`: Valida erro `contract_self_parent` via `ContractService.update`.
- `test_contract_cross_wedding_parent_fails`: Valida bloqueio de pais pertencentes a outro casamento no model.
- `test_create_contract_cross_wedding_parent_raises_error`: Valida bloqueio cross-wedding na criação do serviço.
- `test_contract_circular_parent_fails`: Valida bloqueio de ciclos circulares na árvore de parentesco.
- `test_delete_contract_with_addendums_raises_domain_integrity_error`: Valida a proteção `ProtectedError` na exclusão.
- `test_contract_consolidated_total_selector_ignores_canceled`: Valida a fórmula de soma consolidada ignorando aditivos cancelados.
