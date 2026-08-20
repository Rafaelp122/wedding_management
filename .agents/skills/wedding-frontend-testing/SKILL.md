---
name: wedding-frontend-testing
description: "Frontend testing standards for Wedding Management System — Vitest (isolate: false), React Testing Library, MSW (Orval-generated), Smart/Dumb components, Playwright E2E patterns. Load when writing or reviewing frontend tests."
---

# Wedding Frontend Testing Playbook

Operational testing checklist for Vitest, React Testing Library, MSW, and Playwright E2E.

## Frontend Testing Checklist

- [ ] **Module Isolation & Mocking (`isolate: false`)**: Vitest roda sob `isolate: false`. É PROIBIDO `vi.mock("@/api/generated/...")` com factory síncrona em arquivos de teste. Mocks de data hooks devem ser registrados em `src/test-setup.ts` via `registerMockHook`.
- [ ] **MSW API Integration**: SEMPRE prefira MSW (`server.use(http.METHOD(url, handler))`) utilizando os handlers mock gerados do Orval (`*.msw.ts`).
- [ ] **Async `vi.mock` Fallback**: Se `vi.mock` for estritamente inevitável para controle fino de `isPending`/`loading`, use obrigatoriamente a assinatura assíncrona `async (importOriginal) => ({ ...(await importOriginal<typeof import(...)>()), hookOverride: ... })`.
- [ ] **Imports & Providers**: **SEMPRE** importe `render`, `screen`, `userEvent`, `waitFor` de `@/test-utils` (nunca diretamente de `@testing-library/react`). O `@/test-utils` injeta os providers necessários (`QueryClient`, `Theme`, `Router`, `Toast`).
- [ ] **Mapeamento de Cache de Módulos (Imports)**: Garanta que o caminho de importação do mock no arquivo de teste (`.test.tsx`) seja idêntico ao import do componente real (ex: relativo `../hooks` vs absoluto `@/`) para evitar duplicação no cache do Vite sob `isolate: false`.
- [ ] **Arquitetura Smart vs Dumb Component**: Separe componentes complexos em **Smart Components (Containers)** (gerenciam queries, mutações Orval, rotas) e **Dumb Components (Views)** (renderização pura via props). Teste as Views de forma síncrona sem side-effects.
- [ ] **Funções Puras de Helpers**: Todo cálculo matemático de gráficos, agregação de dados ou formatação complexa deve ficar em funções puras em arquivos utilitários (`utils/`) com testes unitários diretos e rápidos.
- [ ] **Global Mocks & Componentes Especiais**: O `sonner` toast é mockado globalmente em `test-setup.ts` (NUNCA insira `vi.mock("sonner")` por arquivo). Mocke `recharts` com elementos `<div>` simples contendo `data-testid`.
- [ ] **Acessibilidade em Diálogos**: Todo `DialogContent` renderizado DEVE conter `DialogTitle` e `DialogDescription` (utilize `className="sr-only"` para estados de loading/erro/vazio se não visível).
- [ ] **E2E Testing (Playwright)**: Siga o padrão Page Object Model (POM) e fixtures em `tests/e2e/`.
- [ ] **Execution & Standards Reference**:
  - `cd frontend && pnpm test` (Testes de unidade e integração Vitest)
  - `cd frontend && pnpm test:e2e` (Testes E2E Playwright)
  - Documentação de referência: [Frontend Testing Spec](../../../docs/3-reference/testing/frontend-testing-spec.md) | [E2E Testing Spec](../../../docs/3-reference/testing/e2e-testing-spec.md) | [Testing Index](../../../docs/3-reference/testing/index.md), [MSW Patterns](../../../docs/2-how-to/frontend/msw-testing-patterns.md)
