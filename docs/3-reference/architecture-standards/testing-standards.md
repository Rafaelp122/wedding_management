# Especificação Técnica: Padrões e Diretrizes de Testes

> **Módulo:** [architecture-standards](index.md) | [system-overview](../../4-explanation/architecture/system-overview.md)
> **Camada:** Backend (`pytest`) e Frontend (`Vitest`, `RTL`, `Playwright`)

---

## Visão Geral

O **Wedding Management System** exige alta cobertura de testes e aderência rígida à isolação de dados (Multi-tenancy).

---

## Backend: Pytest & Factories

### Regras Críticas (Backend)
1. **PROIBIDO `Model.objects.create()`:** Sempre utilize as factories definidas em `backend/apps/<modulo>/tests/factories.py`.
2. **Isolamento de Service Layer:** Testes de serviço devem ser unitários e isolados, cobrindo fluxos de sucesso e exceções de regras de negócio.
3. **Validação de Multi-tenancy:** Todo teste de serviço deve assegurar que dados de uma `Company` A nunca são acessados ou vazados para a `Company` B.

```python
# Exemplo de teste com Factory
def test_create_expense_success(db):
    company = CompanyFactory()
    wedding = WeddingFactory(company=company)
    expense = ExpenseFactory(company=company, wedding=wedding)

    assert expense.company == company
    assert expense.wedding == wedding
```

---

## Frontend: Vitest, RTL e MSW

### Regras Críticas (Frontend)
1. **Importação via `@/test-utils`:** Sempre importe `render`, `screen`, e `userEvent` de `@/test-utils` para incluir os providers globais (`QueryClientProvider`, `MemoryRouter`).
2. **Mocking Centralizado de Hooks (`isolate: false`):** Mocks globais e hooks do Orval devem ser configurados em `test-setup.ts` usando `registerMockHook`. É **PROIBIDO** utilizar `vi.mock("@/api/generated/...")` individualmente por arquivo de teste.
3. **Sonner & Recharts Mocks:** `toast` do Sonner é mockado globalmente em `test-setup.ts`. Recharts deve ser mockado retornando elementos simples `div` com `data-testid`.
4. **Dialogs & Acessibilidade:** Todo `DialogContent` deve renderizar `DialogTitle` e `DialogDescription` (com `className="sr-only"` em telas de carregamento/erro).

---

## E2E: Playwright

- Testes de fluxo ponta a ponta ficam em `frontend/e2e/`.
- Validam fluxos críticos: Login, Seleção de Casamento, Criação de Fornecedor e Lançamento de Despesa.
