---
title: "Ciclo de Vida do Status do Casamento e Validações (BR-W01 a BR-W06)"
domain: weddings
type: business-rule
source_code:
  - backend/apps/weddings/models.py
  - backend/apps/weddings/services.py
  - backend/apps/weddings/schemas.py
  - backend/apps/weddings/api.py
tests:
  - backend/apps/weddings/tests/test_models.py
  - backend/apps/weddings/tests/test_services.py
  - backend/apps/weddings/tests/test_apis.py
---

# Ciclo de Vida do Status do Casamento e Validações

> **Categoria:** Regra de Negócio (Domínio de Casamentos)
> **Relacionados:** [Catálogo de Regras](../index.md) · [ADR-030: Rich Domain Model](../../adr/030-rich-domain-model-service-layer.md) · [Templates de Cronograma](wedding-schedule-templates.md) · [Regras de Integridade Financeira](../finances/financial-integrity-rules.md) · [Máquina de Estados de Contratos](../logistics/contract-state-machine.md) · [Domínio de Casamentos](../../domains/weddings-domain.md)

---

## 1. Contexto e Invariantes do Domínio

A entidade central `Wedding` encapsula o contexto global de cada casal no sistema. Seguindo o padrão **Rich Domain Model (ADR-030)**, a entidade é responsável por gerenciar sua própria máquina de estados, transições válidas e integridade temporal.

### Invariantes Fundamentais:
1. **Status Canônicos (`StatusChoices`):**
   - `IN_PROGRESS` (Em Andamento): Status padrão atribuído na criação (`default="IN_PROGRESS"`). Permite planejamento ativo, alocação orçamentária, contratação de serviços e agendamentos.
   - `COMPLETED` (Concluído): Indica que o evento foi realizado com sucesso. É um estado terminal.
   - `CANCELED` (Cancelado): Indica a suspensão ou cancelamento do evento. Pode ser reaberto exclusivamente para `IN_PROGRESS`.
2. **Guarda de Conclusão Prematura (BR-W01):** Um casamento só pode ser concluído se a sua data de realização já tiver chegado ou for hoje:

   \[
   d_{\text{wedding}} \le d_{\text{today}}
   \]

   Tentativas de concluir um casamento futuro disparam `BusinessRuleViolation` (`wedding_premature_completion`) ou `ValidationError` no `clean()`.
3. **Validação de Data Futura no Cadastro (BR-W02):** No cadastro ou alteração da data de casamentos em andamento, a data do casamento deve ser maior ou igual à data atual (\(d_{\text{wedding}} \ge d_{\text{today}}\)). Casamentos já concluídos ou históricos preservam suas datas passadas com segurança.
4. **Proteção na Exclusão (BR-W03):** A deleção através de `WeddingService.delete()` valida relacionamentos protegidos. Se existirem contratos ou despesas protegidos (`on_delete=models.PROTECT`), o banco dispara `ProtectedError`, convertido em `DomainIntegrityError('wedding_protected_error')`.
5. **Transições Legais de Estado (BR-W05):** Transições ilegais (como tentar cancelar um casamento já concluído ou transitar de cancelado para concluído diretamente) são rejeitadas com `BusinessRuleViolation` (`wedding_invalid_status_transition`).
6. **Reabertura de Casamento Cancelado (BR-W06):** Casamentos cancelados podem ser reabertos para `IN_PROGRESS` através do método `wedding.reopen()`. É terminantemente proibido reabrir casamentos com status `COMPLETED` (estado terminal definitivo).

---

## 2. Diagrama de Estados e Ciclo de Vida

```mermaid
stateDiagram-v2
    [*] --> IN_PROGRESS : Criação (data >= hoje)
    IN_PROGRESS --> COMPLETED : complete() (data <= hoje)
    IN_PROGRESS --> CANCELED : cancel()
    CANCELED --> IN_PROGRESS : reopen() (BR-W06)

    note right of COMPLETED
        BR-W01: Bloqueia conclusão precoce
        se data > hoje.
        Estado terminal (não pode ser cancelado nem reaberto).
    end note

    note right of CANCELED
        Histórico preservado.
        Permite reabertura se necessário (BR-W06).
    end note
```

---

## 3. Matriz de Regras e Casos de Borda

| Código | Regra de Negócio | Gatilho / Condição | Exceção Lançada | Ação do Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **BR-W01** | **Conclusão Prematura Bloqueada** | Chamar `complete()` ou alterar status para `COMPLETED` quando `wedding.date > timezone.now().date()`. | `BusinessRuleViolation` (`wedding_premature_completion`) | Impede o fechamento indevido de casamentos que ainda não ocorreram. |
| **BR-W02** | **Data Inicial no Futuro** | Criar casamento em andamento com `date < timezone.now().date()`. | `ValidationError` (`date`) | Bloqueia cadastros retroativos acidentais. |
| **BR-W03** | **Proteção de Exclusão** | Exclusão de casamento com contratos ou despesas ativas. | `DomainIntegrityError` (`wedding_protected_error`) | Bloqueia a perda de dados contábeis e contratuais. |
| **BR-W04** | **Ordenação Decrescente** | Listagem padrão via `WeddingQuerySet`. | Nenhuma | Ordena por `-date` (casamentos mais distantes primeiro). |
| **BR-W05** | **Transição Ilegal de Status** | Transição proibida pela máquina de estados (ex.: `COMPLETED -> CANCELED` ou `CANCELED -> COMPLETED`). | `BusinessRuleViolation` (`wedding_invalid_status_transition`) | Impede corrupção do histórico e ciclo de vida do evento. |
| **BR-W06** | **Reabertura de Casamento Cancelado** | Chamar `reopen()` ou tentar reabertura. Válido exclusivamente a partir de `CANCELED`. Bloqueado se `COMPLETED`. | `BusinessRuleViolation` (`wedding_invalid_status_transition`) | Restaura o status para `IN_PROGRESS`, reabilitando o planejamento ativo. |

---

## 4. Implementação e Uso do Modelo de Domínio

### A. Entidade Rica `Wedding` e Governança no Schema (`WeddingOut`)
A lógica de transição e cálculo reside diretamente em [`apps/weddings/models.py`](../../../../backend/apps/weddings/models.py):

- `wedding.complete()`: Conclui o evento validando que a data já chegou.
- `wedding.cancel()`: Cancela o evento caso não esteja concluído.
- `wedding.reopen()`: Retorna um evento cancelado para o status em andamento (`CANCELED -> IN_PROGRESS`), disparando `BusinessRuleViolation('wedding_invalid_status_transition')` se o status atual não for `CANCELED`.
- `wedding.can_transition_to(target_status)`: Consulta a matriz `ALLOWED_TRANSITIONS` e invariantes de data.
- `wedding.get_days_until(reference_date)`: Retorna a quantidade de dias restantes até o casamento.
- `wedding.is_completed`: Propriedade indicando se o evento já foi realizado e concluído.
- `wedding.display_name`: Nome formatado de exibição canônica do casamento.

#### Propriedades Dinâmicas de Governança Expostas na API:
O schema Pydantic [`WeddingOut`](../../../../backend/apps/weddings/schemas.py) expõe diretamente as capacidades de transição para o frontend:
- `allowed_transitions: list[str]`: Lista de transições válidas a partir do estado atual da instância, consultando `ALLOWED_TRANSITIONS`:
  ```python
  @staticmethod
  def resolve_allowed_transitions(obj: "Wedding") -> list[str]:
      return [
          t.value if hasattr(t, "value") else str(t)
          for t in obj.ALLOWED_TRANSITIONS.get(obj.status, [])
      ]
  ```
- `can_complete: bool`: Flag booleana computada indicando se o casamento pode ser concluído no momento presente:
  ```python
  @staticmethod
  def resolve_can_complete(obj: "Wedding") -> bool:
      if hasattr(obj, "can_transition_to"):
          return obj.can_transition_to(WeddingStatusEnum.COMPLETED)
      return False
  ```

```python
# Exemplo canônico de uso do modelo rico:
wedding = wedding_get_selector(company=company, uuid=uuid)

if wedding.can_transition_to(Wedding.StatusChoices.COMPLETED):
    wedding.complete()
    wedding.save()
```

### B. Orquestração no `WeddingService` e Endpoints de API
O serviço em [`apps/weddings/services.py`](../../../../backend/apps/weddings/services.py) coordena transações atômicas, validações de tenant e orquestra a persistência:

- `WeddingService.complete(*, company, instance)`: Caso de uso para conclusão segura, exposto em `POST /api/v1/weddings/{uuid}/complete/` (`operation_id="weddings_complete"`).
- `WeddingService.cancel(*, company, instance)`: Caso de uso para cancelamento com disparo de task assíncrona pós-commit, exposto em `POST /api/v1/weddings/{uuid}/cancel/` (`operation_id="weddings_cancel"`).
- `WeddingService.reopen(*, company, instance)`: Caso de uso semântico para reabertura de casamentos cancelados, exposto em `POST /api/v1/weddings/{uuid}/reopen/` (`operation_id="weddings_reopen"`). Valida tenant, invoca `instance.reopen()`, persiste a alteração e retorna a instância atualizada.
- `WeddingService.update(company, instance, payload)`: Delega atualizações cadastrais e transições de status para `instance.transition_to()`.
- `WeddingService.delete(company, instance)`: Trata proteção relacional com o banco.

---

## 5. Casos de Teste Automatizados (Pytest)

A suíte de testes em `apps/weddings/tests/test_models.py`, `apps/weddings/tests/test_services.py` e `apps/weddings/tests/test_apis.py` valida 100% do ciclo de vida:

- `test_complete_success_on_wedding_day`: Conclusão na data correta.
- `test_complete_fails_when_date_is_future`: Bloqueio de conclusão prematura (BR-W01).
- `test_clean_blocks_completed_to_canceled`: Bloqueio de transição ilegal (BR-W05).
- `test_cancel_success_from_in_progress`: Cancelamento válido a partir de em andamento.
- `test_reopen_success_from_canceled`: Reabertura com sucesso de casamento cancelado (BR-W06).
- `test_wedding_service_reopen_invalid_status_raises`: Bloqueio com HTTP 422 ao tentar reabrir casamento concluído (`COMPLETED`).
- `test_reopen_wedding_api_success`: Validação ponta a ponta do endpoint REST `POST /api/v1/weddings/{uuid}/reopen/`.
- `test_delete_wedding_protected_by_contracts`: Disparo de `DomainIntegrityError` na presença de contratos ativos (BR-W03).
