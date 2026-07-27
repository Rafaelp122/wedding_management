# Como Popular o Banco de Dados Local (Seeding & Templates)

> **Módulo:** [dev-environment](../../2-how-to/dev-environment/index.md) | [weddings-domain](../../4-explanation/domains/weddings-domain.md)
> **Comandos:** `python manage.py seed_db`, `python manage.py seed_wedding_templates`

---

## Visão Geral

Para testar a aplicação localmente com dados verossímeis sem precisar cadastrar informações manualmente pela interface, o sistema oferece dois *Django Management Commands* dedicados ao povoamento do banco de dados.

---

## 1. Populando Templates Oficiais de Cronograma

O comando `seed_wedding_templates` insere no banco de dados os modelos pré-configurados de cronograma (prazos e tarefas típicas de casamento por antecedência):

```bash
# Executando no ambiente virtual do backend
cd backend
uv run python manage.py seed_wedding_templates
```

- **Conteúdo Gerado:** Templates com tarefas organizadas por prazos (12 meses antes, 6 meses antes, 1 mês antes, semana do evento).
- **Idempotência:** O comando verifica a existência de registros existentes antes de inserir, evitando duplicações.

---

## 2. Gerando Dados Fictícios Completos (`seed_db`)

O comando `seed_db` utiliza a biblioteca **Faker** para popular um conjunto completo de dados simulados em todos os módulos do sistema:

```bash
# Executando no backend
cd backend
uv run python manage.py seed_db
```

- **Entidades Criadas:**
  - `Company` e `User` (usuários proprietários e membros ativados).
  - `Wedding` (casamentos com orçamentos e datas configuradas).
  - `BudgetCategory` & `Budget` (categorias com alocações orçamentárias).
  - `Supplier` & `Contract` (fornecedores com CNPJs válidos e contratos).
  - `Expense` & `Installment` (despesas reais e parcelamentos com status `PAID`, `PENDING` ou `OVERDUE`).
  - `Task` & `Event` (checklist operacional e compromissos na agenda do Scheduler).

---

## 3. Limpeza e Re-População

Caso deseje resetar o banco local para um estado limpo e re-popular:

```bash
cd backend
uv run python manage.py flush --no-input
uv run python manage.py migrate
uv run python manage.py seed_wedding_templates
uv run python manage.py seed_db
```
