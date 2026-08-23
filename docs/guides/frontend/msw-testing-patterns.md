# Como Escrever Testes de Frontend com MSW e RTL (Regras de Teste)

> **Módulo:** [frontend-architecture](../../reference/frontend/index.md) | [ui-components-spec](../../reference/frontend/ui-components-spec.md)
> **Stack:** Vitest, React Testing Library, MSW (Mock Service Worker), Orval

---

## Visão Geral e Regra Crítica de Mocks

Para evitar colisões de cache no Vitest quando executado com a flag `isolate: false`, o projeto adota regras estritas sobre interceptação de chamadas de API:

> [!CAUTION]
> **PROIBIDO:** Nunca use `vi.mock("@/api/generated/...", () => ({...}))` com factories síncronas diretamente dentro de arquivos de teste `.test.tsx`. Isso causa duplicação de instâncias de módulos no cache do Vite e falhas intermitentes nos testes.

---

## 1. Padrão Recomendado: Interceptação com MSW (`http`)

Prefira sempre utilizar **MSW (Mock Service Worker)** para simular respostas da API HTTP de forma transparente para as rotas e componentes:

```typescript
import { server } from "@/test-setup";
import { http, HttpResponse } from "msw";
import { render, screen } from "@/test-utils";

test("exibe lista de despesas corretamente", async () => {
  server.use(
    http.get("/api/v1/finances/expenses/", () => {
      return HttpResponse.json([
        { uuid: "123", name: "Buffet Gourmet", actual_amount: "5000.00" },
      ]);
    })
  );

  render(<ExpensesTable />);

  expect(await screen.findByText("Buffet Gourmet")).toBeInTheDocument();
});
```

---

## 2. Padrão para Mocks de Hooks Customizados (`registerMockHook`)

Quando for estritamente necessário interceptar um hook customizado (ex: estados de carregamento `isPending` ou mutações), use o utilitário `registerMockHook` em `test-setup.ts`:

```typescript
// Registre o mock centralizado usando registerMockHook
import { registerMockHook } from "@/test-setup";

registerMockHook("useWeddingDetail", () => ({
  data: { uuid: "123", title: "Casamento Ana & Pedro" },
  isPending: false,
}));
```

---

## 3. Importação de Utilitários (`@/test-utils`)

Sempre importe `render`, `screen` e `userEvent` de `@/test-utils` (nunca diretamente de `@testing-library/react`).

- **Por quê:** O utilitário `@/test-utils` engloba a renderização nos Providers necessários (`QueryClientProvider`, `MemoryRouter`, `ThemeProvider`), garantindo que os componentes funcionem exatamente como em produção.
