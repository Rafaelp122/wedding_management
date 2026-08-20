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

### 2.3 Padrões de Teste para Selectors e Custom QuerySets (`test_selectors.py` e `test_managers.py`)
- **Sem Mock de Banco / ORM:** Selectors e Custom QuerySets DEVEM ser testados contra o banco de dados de teste (`@pytest.mark.django_db`) utilizando Model Factories. **Não fazemos mocking de ORM/Selectors** nesses testes, pois o objetivo é validar a geração real do SQL, anotações (Subqueries, Sum, Coalesce), filtros encadeáveis e comportamento de lazy evaluation.
- **Cobertura Mínima de Selectors:**
  - **Isolamento de Tenant:** Testar que registros de outra `Company` não aparecem na listagem (`for_tenant`).
  - **Filtros e Encadeamento:** Validar filtros opcionais e métodos de escopo (`.pending()`, `.urgent(today)`, etc.).
  - **Resolução 404:** Validar que `*_get_selector` com UUID inexistente ou de outro tenant levanta `ObjectNotFoundError`.

### 2.4 Política de Mocking no Backend
- **O que NUNCA é mockado:**
  - O Django ORM, Models, Custom QuerySets e Selectors em testes de domínio/serviço. Usamos o banco de dados de teste transacional com rollback automático.
- **O que DEVE ser mockado:**
  - Provedores externos de I/O (ex: Cloudflare R2 para upload de contratos, envio de e-mails SES/SMTP, gateways de pagamento, APIs de terceiros).

### 2.5 Isolamento de Multi-Tenancy (HTTP 404)
Todo teste de API ou serviço deve assegurar que requisições acessando recursos de outra `Company` ou de outro `User` retornem estritamente `404 Not Found` (nunca 403 Forbidden ou erro 500 sem tratamento).

### 2.6 Parâmetro `company` Obrigatório
Funções públicas de serviço e seletores devem declarar `company` (ou `company: Company | None = None` para rotas de cron/sistema), auditado automaticamente por `test_security_audit.py`.

### 2.7 Tipagem Estática em Testes (`mypy`)
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
