---
title: "Máquina de Estados de Contratos e Itens Logísticos"
domain: logistics
type: business-rule
source_code:
  - backend/apps/logistics/models/contract.py
  - backend/apps/logistics/models/item.py
  - backend/apps/logistics/services/contract_service.py
tests:
  - backend/apps/logistics/tests/contracts/test_models.py
  - backend/apps/logistics/tests/contracts/test_services.py
  - backend/apps/logistics/tests/items/test_models.py
---

# Máquina de Estados de Contratos e Itens Logísticos

> **Categoria:** Regra de Negócio (Domínio Logístico)
> **Relacionados:** [Hierarquia de Contratos e Aditivos](contract-parent-child-hierarchy.md) · [Validação de CNPJ](cnpj-validation-rules.md) · [Regras de Integridade Financeira](../finances/financial-integrity-rules.md) · [Domínio de Logística](../../domains/logistics-domain.md) · [ADR-030: Rich Domain Model e Validação em 3 Níveis](../../adr/030-rich-domain-model-service-layer.md)

---

## 1. Contexto e Invariantes do Domínio

A gestão de contratos e itens logísticos opera sobre duas **Máquinas de Estados Determinísticas** desacopladas. Enquanto o contrato rege o vínculo jurídico e financeiro com fornecedores, os itens controlam o ciclo operacional de aquisição e entrega física dos bens e serviços no evento.

### Invariantes da Máquina de Contratos (`Contract`):
1. **Transições Canônicas Permitidas (`ALLOWED_TRANSITIONS`):**
   - `DRAFT` (Rascunho) $\rightarrow$ `PENDING`, `CANCELED`.
   - `PENDING` (Pendente de Assinatura) $\rightarrow$ `SIGNED`, `DRAFT`, `CANCELED`.
   - `SIGNED` (Assinado) $\rightarrow$ `CANCELED`.
   - `CANCELED` (Cancelado) $\rightarrow$ `DRAFT`.
2. **Invariantes Estritas do Estado `SIGNED` (BR-L01):** Para formalizar a transição para `SIGNED`, o contrato exige obrigatoriamente:
   - Upload de arquivo válido (`pdf_file` com extensão `.pdf`, `.png`, `.jpg`, `.jpeg` e tamanho $\le 10\text{MB}$ via `MaxFileSizeValidator`).
   - Valor total estritamente positivo ($V_{\text{total}} > 0$).
   - Data de assinatura informada (`signed_date` preenchida).
3. **Desacoplamento de Aquisição e Pagamento (BR-L04):** O status de entrega de um item (`Item.acquisition_status`) evolui de forma independente do pagamento das parcelas financeiras vinculadas.

### Invariantes da Máquina de Itens (`Item`):
- `PENDING` (Pendente) $\longleftrightarrow$ `IN_PROGRESS` (Em Andamento) $\longleftrightarrow$ `DONE` (Entregue/Concluído).

---

## 2. Diagrama de Máquina de Estados (State Diagrams)

### A. Ciclo de Vida do Contrato

```mermaid
stateDiagram-v2
    [*] --> DRAFT : Criação Inicial
    DRAFT --> PENDING : Envio para Assinatura Externa
    DRAFT --> CANCELED : Cancelamento de Negociação
    PENDING --> SIGNED : Assinatura Confirmada (PDF + Valor > 0 + Data)
    PENDING --> DRAFT : Devolução para Revisão
    PENDING --> CANCELED : Desistência
    SIGNED --> CANCELED : Distrato Contratual
    CANCELED --> DRAFT : Reabertura de Negociação
```

### B. Ciclo de Vida do Item Logístico

```mermaid
stateDiagram-v2
    [*] --> PENDING : Item Cadastrado
    PENDING --> IN_PROGRESS : Aquisição em Andamento
    IN_PROGRESS --> DONE : Item Entregue / Concluído
    DONE --> IN_PROGRESS : Reabertura por Ajuste
    IN_PROGRESS --> PENDING : Retorno a Pendente
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Ação do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-L01-A** | **Arquivo Obrigatório em SIGNED** | Transição para `SIGNED` sem arquivo em `pdf_file`. | `ValidationError` | Bloqueia a formalização sem comprovante digital do contrato. |
| **BR-L01-B** | **Valor Positivo em SIGNED** | Transição para `SIGNED` com `total_amount <= 0`. | `ValidationError` | Impede contratos formalizados com valor nulo ou negativo. |
| **BR-L01-C** | **Data de Assinatura Obrigatória** | Transição para `SIGNED` com `signed_date = None`. | `ValidationError` | Exige o registro temporal do ato de assinatura externa. |
| **BR-L01-D** | **Transição Ilegal de Contrato** | Tentativa de transição não mapeada (ex.: `DRAFT -> SIGNED` direto ou `SIGNED -> DRAFT`). | `BusinessRuleViolation` (`contract_invalid_status_transition`) | Rejeita o salto de estado para garantir a esteira de validação. |
| **BR-L04** | **Independência Operacional** | Mudança no status de aquisição do `Item`. | Nenhuma | Atualiza o progresso logístico sem exigir liquidação financeira prévia. |

---

## 4. Implementação e Uso do Modelo de Domínio

### A. Entidade Rica `Contract`
A lógica de transição e invariantes de formalização reside diretamente em [`apps/logistics/models/contract.py`](../../../../backend/apps/logistics/models/contract.py):

- `contract.can_transition_to(target_status)`: Consulta a matriz canônica `ALLOWED_TRANSITIONS`.
- `contract.transition_to(target_status)`: Executa a transição ou dispara `BusinessRuleViolation` (`contract_invalid_status_transition`).
- `contract.send_to_pending()`: Transita para `PENDING`.
- `contract.sign(signed_date=..., pdf_file=...)`: Atribui os dados comprobatórios e transita para `SIGNED`.
- `contract.cancel()`: Distrata o contrato e transita para `CANCELED`.
- `contract.revert_to_draft()`: Retorna o contrato para `DRAFT`.
- `contract._clean_signed_requirements()`: Invariante executada em `clean()`, validando `pdf_file`, `signed_date` e `total_amount > 0`.
- Propriedades com consumidores ativos: `contract.is_addendum` (consumida na UI e serializada em `ContractOut`), `contract.has_file`, `contract.file_name` (propriedades anêmicas de conferência de status como `is_draft`, `is_pending`, `is_signed` e `is_canceled` foram expurgadas em conformidade com YAGNI e ADR-030).

```python
# Exemplo canônico de uso do modelo rico:
contract = contract_get_selector(company=company, uuid=contract_uuid)

if contract.can_transition_to(Contract.StatusChoices.SIGNED):
    contract.sign(signed_date=today, pdf_file=uploaded_file)
    contract.save(update_fields=["status", "signed_date", "pdf_file", "updated_at"])
```

### B. Entidade Rica `Item`
O ciclo de vida operacional e regras de quantidade residem em [`apps/logistics/models/item.py`](../../../../backend/apps/logistics/models/item.py):

- `item.can_transition_to(target_status)`: Consulta transições permitidas para aquisição (`PENDING` $\leftrightarrow$ `IN_PROGRESS` $\leftrightarrow$ `DONE`).
- `item.transition_to(target_status)`: Executa a transição ou dispara `BusinessRuleViolation` (`item_invalid_status_transition`).
- `item.start()`: Inicia o processo de aquisição (`IN_PROGRESS`).
- `item.complete()`: Marca o item como concluído/entregue (`DONE`).
- `item.reopen()`: Reabre item concluído para `IN_PROGRESS`.
- `item.revert_to_pending()`: Retorna o item para `PENDING`.
- Observação: propriedades anêmicas de status (`is_pending`, `is_in_progress`, `is_done`) foram expurgadas do modelo por ausência de consumidores reais (YAGNI).

### C. Orquestração no `ContractService` e `ItemService`
A camada de serviços em [`apps/logistics/services/`](../../../../backend/apps/logistics/services/) orquestra autorização multi-tenant e persistência cirúrgica com `update_fields`:

- `ContractService.transition_status(company, uuid, status_input)`: Valida permissão do tenant, executa `contract.transition_to(status_input)` e persiste estritamente com `update_fields=["status", "updated_at"]`.
- `ContractService.sign(company, instance, ...)` / `send_to_pending` / `cancel` / `revert_to_draft`: Casos de uso semânticos para formalização e distrato.
- `ItemService.start(company, instance)` / `complete` / `reopen` / `revert_to_pending`: Orquestração do ciclo operacional do item.

### D. Endpoints Semânticos de API (Django Ninja)
Em conformidade com a ADR-030 e o Rich Domain Model, os roteadores expõem ações semânticas diretas:
- **Contratos (`apps/logistics/api/contracts.py`):**
  - `POST /contracts/{uuid}/send-to-pending/` (`logistics_contracts_send_to_pending`)
  - `POST /contracts/{uuid}/sign/` (`logistics_contracts_sign`)
  - `POST /contracts/{uuid}/cancel/` (`logistics_contracts_cancel`)
  - `POST /contracts/{uuid}/revert-to-draft/` (`logistics_contracts_revert_to_draft`)
- **Itens (`apps/logistics/api/items.py`):**
  - `POST /items/{uuid}/start/` (`logistics_items_start`)
  - `POST /items/{uuid}/complete/` (`logistics_items_complete`)
  - `POST /items/{uuid}/reopen/` (`logistics_items_reopen`)
  - `POST /items/{uuid}/revert-to-pending/` (`logistics_items_revert_to_pending`)

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes unitários em `apps/logistics/tests/contracts/test_models.py` e `apps/logistics/tests/contracts/test_services.py` valida 100% dos caminhos e bloqueios da máquina de estados:

- `test_valid_transitions`: Valida todas as 7 transições permitidas no ciclo de vida da entidade.
- `test_invalid_transitions`: Valida rejeição com `BusinessRuleViolation` (`contract_invalid_status_transition`) para transições proibidas (ex.: `DRAFT -> SIGNED`, `SIGNED -> DRAFT`, `CANCELED -> SIGNED`).
- `test_signed_without_pdf_fails`: Valida exigência do arquivo PDF para contratos assinados via `full_clean()`.
- `test_signed_without_positive_amount_fails`: Valida exigência de valor estritamente positivo.
- `test_signed_without_signed_date_fails`: Valida exigência da data de formalização.
- `test_transition_to_signed_without_pdf_raises_error`: Valida propagação de erro de negócio no `ContractService.transition_status`.
- `test_contract_semantic_lifecycle`: Valida métodos semânticos (`send_to_pending`, `sign`, `cancel`, `revert_to_draft`).
