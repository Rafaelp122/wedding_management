# PR 4 — Remover `select_related("company")` redundante

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Remover `select_related("company")` desnecessário do `SupplierService.list()`.

**Architecture:** O `company` field em `TenantModel` já armazena `company_id` como integer. Nenhum caller acessa `supplier.company` (o objeto) — o schema `SupplierOut` não inclui `company`.

**Tech Stack:** Django ORM, pytest

---

## Contexto

### Por que `select_related("company")` é redundante

O `SupplierService.list()` faz:
```python
qs = Supplier.objects.for_tenant(company).select_related("company")
```

O `select_related("company")` faz um JOIN na tabela `companies` para pré-carregar o objeto `Company`. Mas:

1. **`for_tenant(company)`** já filtra por `WHERE company_id = X` usando o PK da instância `company` carregada em memória. Nenhuma query adicional é feita.

2. **`Supplier.company_id`** (o integer) já está disponível sem query — é um campo FK armazenado diretamente na tabela `suppliers`.

3. **`SupplierOut` schema** não serializa `company`:
   ```python
   class SupplierOut(Schema):
       uuid: UUID4
       name: str
       cnpj: str
       phone: str
       email: str
       is_active: bool
       address: str
       city: str
       state: str
       website: str
       notes: str
       created_at: datetime.datetime
       updated_at: datetime.datetime
       # ← NENHUM campo company
   ```

4. **Nenhum caller** acessa `supplier.company` no path de listagem. O único acesso é em um teste de create (`assert supplier.company == user.company`), que não usa o `list()`.

### Consequência

O `select_related("company")` gera um JOIN desnecessário na tabela `companies` a cada query de listagem. É uma query extra (ou JOIN extra) que não agrega valor.

---

## Arquivos que vão mudar

| Arquivo | Mudança |
|---|---|
| `backend/apps/logistics/services/supplier_service.py:30` | Remover `.select_related("company")` |

---

## Task 1: Remover `select_related("company")`

**Objective:** Eliminar JOIN desnecessário na tabela `companies`.

**Files:**
- Modify: `backend/apps/logistics/services/supplier_service.py:30`
- Test: `backend/apps/logistics/tests/suppliers/test_services.py::TestSupplierServiceListAndGet` (existentes)

**Step 1: Modificar `list()`**

```python
# ANTES (supplier_service.py:30)
qs = Supplier.objects.for_tenant(company).select_related("company")

# DEPOIS
qs = Supplier.objects.for_tenant(company)
```

**Step 2: Verificar que testes passam**

Run: `cd backend && python -m pytest apps/logistics/tests/suppliers/test_services.py::TestSupplierServiceListAndGet -v`
Expected: Todos passam

**Step 3: Commit**

```bash
git add backend/apps/logistics/services/supplier_service.py
git commit -m "fix(logistics): remove redundant select_related in SupplierService.list"
```

---

## Task 2: Verificação final

**Objective:** Rodar suíte completa de suppliers e lint.

**Step 1: Rodar todos os testes de suppliers**

Run: `cd backend && python -m pytest apps/logistics/tests/suppliers/ -v --tb=short`
Expected: Todos passam

**Step 2: Rodar testes de API de suppliers**

Run: `cd backend && python -m pytest apps/logistics/tests/test_apis.py -v --tb=short -k "supplier"`
Expected: Todos passam

**Step 3: Rodar lint**

Run: `make lint` ou `ruff check .`
Expected: Sem erros novos

---

## Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Algum serializer/template pode acessar `supplier.company.name` | Verificado: `SupplierOut` não inclui `company`. Nenhum caller no path de listagem acessa `supplier.company` |
| `for_tenant()` pode precisar do JOIN para ordenação | Não: `for_tenant()` apenas adiciona `WHERE company_id = X`. Ordenação é por `name` (meta do model) |

## Resultado Esperado

| Métrica | Antes | Depois |
|---|---|---|
| JOINs na query de listagem | 1 extra (companies) | 0 |
| Queries para listar suppliers | 1 (com JOIN) | 1 (sem JOIN) |
| Retorno da API | Idêntico | Idêntico |
