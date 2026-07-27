# Regra de Negócio: Máquina de Estados de Contratos e Itens Logísticos

> **Módulo:** [logistics-domain](../../domains/logistics-domain.md) | [contract-model](../../../3-reference/models/logistics/contract-model.md)
> **Código:** `backend/apps/logistics/models/contract.py`, `backend/apps/logistics/models/item.py`

---

## 1. Máquina de Estados de Contratos (`Contract.ALLOWED_TRANSITIONS`)

A entidade `Contract` possui quatro status possíveis com transições estritamente controladas:

```text
[DRAFT] <------> [PENDING] -------> [SIGNED]
   |                |                  |
   +----------------+------------------+-----> [CANCELED]
```

### Transições Permitidas:
- `DRAFT` (Rascunho): Pode evoluir para `PENDING` ou `CANCELED`.
- `PENDING` (Pendente de Assinatura): Pode transitar para `SIGNED`, voltar para `DRAFT` ou ir para `CANCELED`.
- `SIGNED` (Assinado): Estado final de formalização. Pode transitar para `CANCELED` em caso de distrato.
- `CANCELED` (Cancelado): Pode retornar para `DRAFT` para reabertura de negociação.

### Travas de Segurança no Status `SIGNED` (`clean()`):
Para que um contrato transite para `SIGNED`, o modelo exige obrigatoriamente:
1. `pdf_file` preenchido (upload do documento PDF ou imagem do contrato assinado).
2. `total_amount > 0` (valor de face positivo).
3. `signed_date` informada (data de formalização externa).

---

## 2. Máquina de Estados de Itens Logísticos (`Item.ALLOWED_TRANSITIONS`)

A entidade `Item` gerencia o ciclo de entrega de bens e serviços contratados:

```text
[PENDING] <------> [IN_PROGRESS] <------> [DONE]
```

### Transições Permitidas:
- `PENDING` (Pendente): Estado inicial. Transita para `IN_PROGRESS`.
- `IN_PROGRESS` (Em Andamento): Transita para `DONE` (concluído) ou retorna para `PENDING`.
- `DONE` (Concluído): Item/serviço entregue no evento. Pode retornar para `IN_PROGRESS` se houver reajuste.
