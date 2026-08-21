---
title: "Hierarquia Pai-Filho e Aditivos de Contratos"
domain: logistics
type: business-rule
code: backend/apps/logistics/services/contract_service.py
tests: backend/apps/logistics/tests/contracts/test_services.py
---

# Regra de Negócio: Hierarquia de Contratos e Termos Aditivos

> **Módulo:** [logistics-domain](../../domains/logistics-domain.md) | [contract-model](../../../3-reference/models/logistics/contract-model.md)
> **Código:** `backend/apps/logistics/models/contract.py`, `backend/apps/logistics/services/contract_service.py` (`_resolve_parent`, `calculate_total_with_addendums`)

---

## 1. Relação Pai/Filho (`parent`)

O modelo `Contract` permite vincular um contrato como filho de outro através do campo `parent`:
- **Utilidade:** Representação de Termos Aditivos, reajustes e adendos contratuais.
- **Relacionamento no Banco:** `ForeignKey("self", on_delete=models.PROTECT, related_name="addendums")`.

---

## 2. Travas de Segurança da Hierarquia (`Contract.clean()` e `ContractService`)

Ao criar ou atualizar um contrato pai, o sistema aplica quatro travas de segurança atômicas no modelo e na camada de serviço:

1. **Bloqueio de Auto-vínculo:** Um contrato não pode ser pai de si mesmo (`contract_self_parent`).
2. **Bloqueio Cross-Wedding:** O contrato pai deve pertencer obrigatoriamente ao mesmo casamento (`wedding_id`) do aditivo (`contract_cross_wedding_parent`).
3. **Prevenção de Ciclos no Grafo (Graph Cycle Guard):** O sistema percorre a árvore de ancestrais para garantir que o contrato pai selecionado não seja um descendente do contrato atual (`contract_circular_parent`).
4. **Proteção na Exclusão (`ProtectedError`):** A exclusão física de um contrato principal que possua termos aditivos filhos ativos é bloqueada pelo banco de dados. O serviço dispara `DomainIntegrityError` (`contract_protected_by_addendums`) exigindo a remoção prévia dos aditivos.

---

## 3. Cálculo Consolidado de Contratos e Aditivos (`ContractService.calculate_total_with_addendums`)

Para exibir o compromisso financeiro real de uma contratação com aditivos:
- **Fórmula:** `Valor Consolidado = Valor Contrato Principal + Σ(Valor dos Termos Aditivos Ativos)`.
- **Regra de Aditivos Cancelados:** Aditivos com status `CANCELED` são automaticamente desconsiderados do somatório consolidado.
- **Otimização de Consulta (Anti N+1):** O `ContractQuerySet.with_totals()` anota o total de aditivos (`addendums_total_amount`) diretamente no banco via `Subquery`, e o schema `ContractOut` expõe `addendums_total_amount` e `total_amount_with_addendums`.
