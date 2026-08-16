# Especificação Técnica: Padrões de Teste Backend (`pytest`)

> **Módulo:** [testing](index.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)
> **Camada:** Backend (`pytest` + Factories + Django Ninja)

---

## 1. Visão Geral

Os testes backend no **Wedding Management System** garantem a integridade das regras de negócio, a isolação estrita de multi-tenancy e a estabilidade da camada de serviços (`services.py`).

---

## 2. Regras Críticas

### 2.1 PROIBIDO `Model.objects.create()` em Testes
Sempre utilize as Model Factories configuradas em `backend/apps/<modulo>/tests/factories.py` (ex: `WeddingFactory(company=user.company)`).
O uso direto de `.objects.create()` é proibido em testes para evitar contornar validações do `BaseModel` ou gerar relacionamentos inválidos.

```python
# ✅ CORRETO
def test_create_expense_success(db):
    company = CompanyFactory()
    wedding = WeddingFactory(company=company)
    expense = ExpenseFactory(company=company, wedding=wedding)

    assert expense.company == company
    assert expense.wedding == wedding
```

### 2.2 Isolamento da Camada de Serviços (`services.py`)
- Testes em `services.py` devem ser unitários, isolados e passar objetos `Company` explícitos.
- Toda função pública em `services.py` DEVE possuir no mínimo:
  - **1 teste de sucesso (happy path)**.
  - **1 teste de falha (sad path / exceção de regra de negócio)**.

```python
@pytest.mark.django_db
class TestExpenseServiceCreate:
    def test_create_expense_success(self, user):
        expense = ExpenseService.create_expense(
            company=user.company,
            wedding=user.wedding,
            name="Buffet",
            amount=Decimal("5000.00"),
        )
        assert expense.company == user.company
        assert expense.id is not None

    def test_create_expense_failure_other_tenant(self, user):
        other_company = CompanyFactory()
        with pytest.raises(ObjectNotFoundError):
            ExpenseService.create_expense(
                company=other_company,
                wedding=user.wedding,
                name="Buffet",
                amount=Decimal("5000.00"),
            )
```

### 2.3 Isolamento de Multi-Tenancy (HTTP 404)
Todo teste de API ou serviço deve assegurar que requisições acessando recursos de outra `Company` ou de outro `User` retornem estritamente `404 Not Found` (nunca 403 Forbidden ou erro 500 sem tratamento).

### 2.4 Parâmetro `company` Obrigatório
Funções públicas de serviço devem declarar `company` (ou `company: Company | None = None` para rotas de cron/sistema), auditado automaticamente por `test_security_audit.py`.

### 2.5 Tipagem Estática em Testes (`mypy`)
- Toda função e método de teste deve declarar anotação explícita de retorno `-> None` e tipagem em parâmetros e fixtures.
- O projeto configura explicitamente `disallow_untyped_calls = false` nos overrides da suíte de testes devido à natureza dinâmica das factories do `factory_boy`, garantindo checagem estrita de definições (`disallow_untyped_defs = true`) e de corpo (`check_untyped_defs = true`) sem exigir anotações artificiais nas instanciações de factories.

---

## 3. Estrutura de Arquivos e Nomenclatura

- **Estrutura**: `apps/<modulo>/tests/test_models.py`, `test_services.py`, `test_apis.py`.
- **Nomenclatura**:
  - Classe: `Test<Entidade><Camada>` (ex: `TestExpenseServiceCreate`)
  - Método: `test_<comportamento>_<cenario>_<resultado_esperado>` (ex: `test_create_expense_failure_other_tenant`)

---

## 4. Execução de Testes

```bash
cd backend && .venv/bin/pytest apps/<modulo>/
```
