# Especificação Técnica: Padrões de Teste Frontend (`Vitest`, `RTL`, `MSW`)

> **Módulo:** [testing](index.md) | [ci-cd-pipeline-flow](../../architecture/concepts/ci-cd-pipeline-flow.md)
> **Camada:** Frontend (`Vitest` + React Testing Library + MSW)

---

## 1. Visão Geral

Os testes de unidade e integração no frontend garantem a robustez dos componentes React, acessibilidade (A11y), integração de rotas e sincronização de dados via TanStack Query.

---

## 2. Arquitetura de Execução (`isolate: false`)

O Vitest executa com `isolate: false` para maximizar a performance. Sob esta configuração:
- O estado de módulos é compartilhado entre testes do mesmo processo.
- É **PROIBIDO** utilizar `vi.mock("@/api/generated/...", () => ({...}))` com factory síncrona dentro de arquivos de teste para evitar colisão de mocks.
- Todos os mocks globais de hooks devem ser registrados em `src/test-setup.ts` usando `registerMockHook` ou interceptados via MSW.

---

## 3. Estratégias de Mocking de API

### 3.1 MSW (Mock Service Worker) — Testes de Integração (RECOMENDADO)
Utilize os handlers do MSW gerados pelo Orval em `src/api/generated/v1/endpoints/*/*.msw.ts`.

Para cenários de erro ou retornos específicos em testes individuais:
```tsx
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

test("exibe mensagem de erro em falha da API", async () => {
  server.use(
    http.get("/api/v1/finances/expenses/", () =>
      HttpResponse.json({ detail: "Erro interno" }, { status: 500 })
    )
  );

  render(<WeddingFinancesView weddingUuid="w-1" />);
  expect(await screen.findByText(/erro interno/i)).toBeInTheDocument();
});
```

### 3.2 Async `vi.mock` Fallback (Casos Especiais)
Se `vi.mock` for estritamente necessário para controlar estados como `isPending` ou `isLoading`, utilize obrigatoriamente a assinatura assíncrona com `importOriginal`:
```tsx
vi.mock("@/api/generated/v1/endpoints/weddings/weddings", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/api/generated/v1/endpoints/weddings/weddings")>();
  return {
    ...actual,
    useWeddingsList: () => ({ data: undefined, isLoading: true }),
  };
});
```

---

## 4. Importações e Providers (`@/test-utils`)

**SEMPRE** importe utilitários de teste de `@/test-utils` (nunca diretamente de `@testing-library/react`):
```tsx
// CORRETO
import { render, screen, userEvent, waitFor } from "@/test-utils";
```
O `@/test-utils` injeta automaticamente os providers globais (`QueryClientProvider`, `ThemeProvider`, `RouterProvider`, `Toaster`).

---

## 5. Componentes Radix UI Portals e Acessibilidade

- Componentes como `Dialog`, `Sheet` e `DropdownMenu` renderizam em portais Radix fora do container padrão.
- Utilize `within(screen.getByRole("dialog"))` para buscar elementos dentro do portal.
- Todo `DialogContent` renderizado DEVE conter `DialogTitle` e `DialogDescription` (use `className="sr-only"` se for invisível).

---

## 6. Arquitetura Smart vs Dumb Components

- **Smart Components (Containers)**: Encapsulam hooks Orval/TanStack Query, leitura de rotas e formulários.
- **Dumb Components (Presenters/Views)**: Síncronos, puramente visuais, recebendo callbacks via props. Permite testes unitários simples e ultrarrápidos.

---

## 7. Execução de Testes

```bash
cd frontend && pnpm test
```
