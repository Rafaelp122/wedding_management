# How-To: Executando a Management Command de Parcelas Vencidas

> **Objetivo:** Executar manualmente ou agendar o recálculo do status das parcelas vencidas.

---

## Executando o Comando

```bash
cd backend
uv run python manage.py mark_overdue_installments
```

O comando irá:
1. Buscar todas as parcelas com `status='PENDING'` cuja `due_date` seja menor que a data atual.
2. Atualizar o status para `OVERDUE`.
3. Recalcular o status consolidado das despesas filhas.
