# Regra de Negócio: Integração de Pagamentos com a Agenda de Compromissos (BR-S01)

> **Módulo:** [finances-domain](../../domains/finances-domain.md) | [scheduler-domain](../../domains/scheduler-domain.md)
> **Código:** `backend/apps/finances/services/installment_service.py` (`_create_payment_events`, `_delete_payment_events_for_expense`)

---

## 1. Auto-geração de Eventos de Pagamento (BR-S01)

Sempre que parcelas (`Installment`) são geradas automaticamente para uma despesa (via `InstallmentService.auto_generate_installments`), o sistema cria simultaneamente um evento no módulo `scheduler` para cada parcela:

- **Tipo do Evento:** `event_type = "pagamento"`
- **Vínculo:** `source_installment = installment`
- **Data/Hora:** Data de vencimento da parcela às 09:00:00 AM (`timezone.make_aware`).
- **Título Padronizado:** `Pagamento: {expense.name} - Parcela {i}/{N}`

Esses eventos aparecem automaticamente no calendário do evento para que o cerimonialista visualize as datas críticas de desembolso financeiro.

---

## 2. Limpeza Transacional em Cascata

Quando parcelas são redistribuídas ou uma despesa/parcela é excluída:
- A função privada `_delete_payment_events_for_expense()` executa em transação atômica (`@transaction.atomic`), removendo todos os eventos de pagamento associados do banco de dados antes de excluir as parcelas.
- Isso previne a permanência de eventos órfãos de pagamento na agenda do casamento.
