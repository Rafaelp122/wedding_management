---
title: "Templates de Cronograma do Casamento"
domain: weddings
type: business-rule
code: backend/apps/weddings/services.py
tests: backend/apps/weddings/tests/test_services.py
---

# Regra de Negócio: Aplicação de Templates de Cronograma

> **Módulo:** [weddings-domain](../../domains/weddings-domain.md) | [scheduler-domain](../../domains/scheduler-domain.md)
> **Código:** `backend/apps/weddings/services.py` (`_apply_template_events`)


---

## 1. Funcionamento dos Templates

Ao criar um casamento via `WeddingService.create()`, o parâmetro opcional `template` (ex: `"padrao_12_meses"`) pode ser fornecido para agendar automaticamente uma série de compromissos pré-configurados na agenda do evento.

---

## 2. Cálculo Relativo de Datas (`offset_days`)

Cada compromisso dentro de um template define um valor `offset_days` que representa a quantidade de dias *antes* da data do casamento em que o evento deve ser agendado.

A data de início do evento é calculada da seguinte forma:

```text
data_evento = data_casamento - offset_days
horario_inicio = 09:00 AM (fuso horário configurado)
```

### Exemplo:
- **Data do Casamento:** `2026-12-15`
- **Offset do Evento ("Degustação de Buffet"):** `180` dias
- **Data Gerada do Evento:** `2026-06-18` às `09:00:00`

---

## 3. Transacionalidade e Isolamento

- A aplicação do template ocorre em transação atômica (`@transaction.atomic`). Se a criação de qualquer evento do template falhar, toda a operação de criação do casamento é revertida.
- A criação passa pela flag `_allow_historical_start=True` no `EventService` para permitir agendamentos com data relativa se a data do casamento estiver próxima.
