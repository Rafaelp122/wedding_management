# Como Executar a Suíte de Testes Pytest no Backend

> **Categoria:** [backend](../../reference/architecture-standards/index.md) | [backend-testing-spec](../../reference/testing/backend-testing-spec.md) | [use-core-services](use-core-services.md)
> **Stack & Ferramentas:** Pytest, `pytest-django`, `pytest-xdist`, `pytest-cov`, FactoryBoy

---

## Visão Geral

A suíte de testes backend do **Wedding Management System (WMS)** é construída com foco em isolamento multi-tenant, determinismo e alta performance de execução.

> [!IMPORTANT]
> **REGRA DE TESTES BACKEND:** É estritamente **PROIBIDO** utilizar chamadas diretas como `Model.objects.create(...)` dentro dos testes.
> Utilize sempre as **factories** centralizadas em `apps/<modulo>/tests/factories.py` (ex: `UserFactory`, `CompanyFactory`, `WeddingFactory`, `ExpenseFactory`).

---

## Passo 1: Execução Básica da Suíte de Testes

Para executar toda a suíte de testes no ambiente local:

```bash
# Executando no container Docker via Makefile:
make test

# Ou diretamente no terminal do Host com uv:
cd backend
uv run pytest -v
```

---

## Passo 2: Filtragem Granular de Testes

O Pytest oferece diversas opções para rodar subconjuntos específicos de testes durante o ciclo de desenvolvimento:

### 1. Por Módulo ou Domínio (App)
```bash
uv run pytest apps/finances/
uv run pytest apps/logistics/
uv run pytest apps/scheduler/
```

### 2. Por Arquivo de Teste
```bash
uv run pytest apps/finances/tests/test_services.py
uv run pytest apps/core/tests/test_api_architecture.py
```

### 3. Por Nome ou Padrão de Teste (`-k`)
Executa apenas testes cujo nome case-insensitive contenha a expressão:
```bash
uv run pytest -k "test_mark_overdue"
uv run pytest -k "test_installment and not test_delete"
```

### 4. Por Marcadores (`-m`)
```bash
# Executar testes que requerem acesso ao banco de dados:
uv run pytest -m django_db

# Executar apenas testes de integração:
uv run pytest -m integration
```

---

## Passo 3: Execução Paralela com `pytest-xdist`

Para acelerar significativamente o tempo total da suíte, utilize o plugin `pytest-xdist` para distribuir a execução entre os núcleos da CPU:

```bash
# Utilizar automaticamente todos os núcleos disponíveis:
uv run pytest -n auto

# Ou especificar uma quantidade fixa de workers:
uv run pytest -n 4
```

> [!NOTE]
> Cada worker do `pytest-xdist` recebe seu próprio banco de dados de teste isolado (ex: `test_wedding_db_gw0`, `test_wedding_db_gw1`), prevenindo condições de corrida entre testes concorrentes.

---

## Passo 4: Relatórios de Cobertura de Código (`pytest-cov`)

Para medir a cobertura da suíte sobre o código de domínio (`apps/`):

```bash
# Relatório resumido no terminal via Makefile:
make test-cov

# Gerar relatório detalhado em HTML:
cd backend
uv run pytest --cov=apps --cov-report=html
```

*O relatório HTML interativo será salvo em `backend/htmlcov/index.html`.*

---

## Passo 5: Debugging Interativo com PDB

Quando um teste falhar ou você precisar inspecionar variáveis em tempo de execução:

1. **Insira um ponto de interrupção no código:**
   ```python
   breakpoint()  # ou import pdb; pdb.set_trace()
   ```

2. **Execute o teste com as flags `-s` (sem captura de stdout) e `--pdb`:**
   ```bash
   uv run pytest apps/finances/tests/test_services.py -k "test_create" -s --pdb
   ```

---

## Passo 6: Padrão de Escrita com Factories e Tenants

Exemplo canônico de um teste unitário de serviço respeitando o isolamento multi-tenant:

```python
# backend/apps/finances/tests/test_services.py
import pytest
from apps.finances.services.budget_service import BudgetService
from apps.finances.schemas import BudgetIn
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.tests.factories import WeddingFactory

@pytest.mark.django_db
def test_create_budget_for_wedding_success():
    # 1. Setup com Factories
    company = CompanyFactory()
    wedding = WeddingFactory(company=company)
    payload = BudgetIn(wedding=wedding.uuid, total_budget=120000)

    # 2. Execução do Serviço
    budget = BudgetService.create(company=company, payload=payload)

    # 3. Asserções
    assert budget.uuid is not None
    assert budget.company == company
    assert budget.wedding == wedding
    assert budget.total_budget == 120000
```

---

## Troubleshooting & Resolução de Problemas

### 1. Erro de Banco de Testes Não Sincronizado
- **Sintoma:** `django.db.utils.ProgrammingError: relation "..." does not exist`.
- **Causa:** O banco de testes em cache não contém as últimas migrações geradas.
- **Solução:** Force a recriação do schema de testes com a flag `--create-db`:
  ```bash
  uv run pytest --create-db
  ```

### 2. Testes Lentos na Suíte
- **Sintoma:** A suíte está demorando muito tempo para concluir.
- **Solução:** Identifique os 10 testes mais lentos com a flag `--durations`:
  ```bash
  uv run pytest --durations=10
  ```
