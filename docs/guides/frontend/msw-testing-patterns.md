# Como Escrever Testes de Frontend com MSW e RTL

> **Categoria:** [frontend](../../reference/frontend/index.md) | [frontend-testing-spec](../../reference/testing/frontend-testing-spec.md) | [ui-components-spec](../../reference/frontend/ui-components-spec.md)
> **Stack:** Vitest (`isolate: false`), React Testing Library (RTL), Mock Service Worker (MSW), Orval

---

## Visão Geral e Regra Crítica de Isolamento

Para garantir máxima velocidade de execução na suíte de testes do frontend, o Vitest é configurado com a flag `isolate: false`. Sob este modo, todos os arquivos de teste compartilham o mesmo contexto de módulos do Vite.

> [!CAUTION]
> **REGRA INVIOLÁVEL:** Nunca utilize `vi.mock("@/api/generated/...", () => ({...}))` dentro de arquivos de teste individuais `.test.tsx`.
> Mocks dinâmicos locais causam poluição de memória, efeitos colaterais entre arquivos executados em paralelo e falhas intermitentes no CI.

### O Padrão Oficial do Projeto: MSW
A interceptação de requisições de API **DEVE** ocorrer exclusivamente no nível de rede através do **Mock Service Worker (MSW)**. Dessa forma, testamos os componentes reais integrados com os hooks do Orval e com o cache do TanStack Query sem alterar a integridade dos módulos.

---

## Passo 1: Importação de Utilitários de Teste

Sempre importe `render`, `screen`, `waitFor`, `userEvent` e `server` de `@/test-utils` (e nunca diretamente de `@testing-library/react`):

```typescript
import { describe, expect, it, beforeEach } from "vitest";
import { render, screen, waitFor, server, userEvent } from "@/test-utils";
import { http, HttpResponse } from "msw";
```

> [!NOTE]
> O utilitário `render` do `@/test-utils` envolve automaticamente o componente nos providers essenciais: `QueryClientProvider`, `MemoryRouter`, `ThemeProvider` e `TooltipProvider`.

---

## Passo 2: Padrões Práticos de Testes

### 1. Teste de Consulta e Renderização com Sucesso (GET 200)

```tsx
import { describe, it, expect } from "vitest";
import { render, screen, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { WeddingBudgetSummary } from "@/features/finances/components/WeddingBudgetSummary";

describe("WeddingBudgetSummary", () => {
  it("renderiza o valor total do orçamento retornado pela API", async () => {
    // 1. Configurar resposta mockada via MSW
    server.use(
      http.get("*/api/v1/finances/budgets/", () => {
        return HttpResponse.json({
          items: [{ uuid: "b1", total_budget: 150000, total_spent: 45000 }],
          count: 1,
        });
      })
    );

    // 2. Renderizar o componente
    render(<WeddingBudgetSummary weddingUuid="wedding-123" />);

    // 3. Asserir exibição assíncrona com findByText
    expect(await screen.findByText("R$ 150.000,00")).toBeInTheDocument();
    expect(screen.getByText("R$ 45.000,00")).toBeInTheDocument();
  });
});
```

---

### 2. Teste de Tratamento de Erro da API (HTTP 500)

```tsx
it("exibe mensagem amigável quando a API retorna erro interno", async () => {
  server.use(
    http.get("*/api/v1/finances/budgets/", () => {
      return HttpResponse.json(
        { message: "Erro interno no servidor de banco de dados." },
        { status: 500 }
      );
    })
  );

  render(<WeddingBudgetSummary weddingUuid="wedding-123" />);

  expect(
    await screen.findByText("Erro ao carregar dados do orçamento.")
  ).toBeInTheDocument();
});
```

---

### 3. Teste de Estado de Carregamento (Loading Skeletons)

Para testar o estado de carregamento sem resolver a requisição imediatamente, retorne uma Promise pendente:

```tsx
it("exibe o skeleton animado enquanto os dados estão sendo carregados", () => {
  server.use(
    http.get("*/api/v1/finances/budgets/", () => new Promise(() => {}))
  );

  render(<WeddingBudgetSummary weddingUuid="wedding-123" />);

  const skeletons = document.querySelectorAll(".animate-pulse");
  expect(skeletons.length).toBeGreaterThanOrEqual(1);
});
```

---

### 4. Teste de Mutação, Interação de Formulário e Toasts (POST 201)

```tsx
it("submete formulário de fornecedor e exibe toast de sucesso", async () => {
  let payloadRecebido: unknown = null;

  server.use(
    http.post("*/api/v1/logistics/suppliers/", async ({ request }) => {
      payloadRecebido = await request.json();
      return HttpResponse.json(
        { uuid: "sup-99", name: "Buffet Real", cnpj: "12.345.678/0001-90" },
        { status: 201 }
      );
    })
  );

  const user = userEvent.setup();
  render(<CreateSupplierDialog onSuccess={() => {}} />);

  // Preencher campos
  await user.type(screen.getByLabelText(/Nome do Fornecedor/i), "Buffet Real");
  await user.type(screen.getByLabelText(/CNPJ/i), "12.345.678/0001-90");
  await user.type(screen.getByLabelText(/Categoria/i), "Gastronomia");

  // Submeter
  await user.click(screen.getByRole("button", { name: /Salvar Fornecedor/i }));

  // Validar recepção do payload
  await waitFor(() => {
    expect(payloadRecebido).toMatchObject({
      name: "Buffet Real",
      cnpj: "12.345.678/0001-90",
    });
  });
});
```

---

## Passo 3: Mocks de Bibliotecas Visuais em `test-setup.ts`

Componentes gráficos complexos (como `recharts`) ou provedores externos (como `@react-oauth/google` e `sonner`) são mockados de forma global e centralizada em `src/test-setup.ts`.

Ao final de cada teste, o `test-setup.ts` executa automaticamente:
```typescript
afterEach(() => {
  cleanup();
  server.resetHandlers(); // Restaura handlers padrão do MSW
  vi.clearAllMocks();
});
```

---

## Troubleshooting & Resolução de Problemas

### 1. Alerta `[MSW] Warning: captured a request without a matching request handler`
- **Causa:** O endpoint requisitado pelo hook não correspondeu a nenhum handler do `server.use`.
- **Solução:** Utilize wildcards na URL (ex: `http.get("*/api/v1/modulo/endpoint/", ...)`), garantindo que tanto URLs relativas quanto absolutas sejam capturadas.

### 2. Falhas Intermitentes com `waitFor` / `findBy*`
- **Causa:** O componente realiza múltiplos re-renders assíncronos ou a asserção foi executada antes da finalização do ciclo de microtasks.
- **Solução:** Utilize `await screen.findByText(...)` para elementos que dependem de dados remotos em vez de `screen.getByText(...)`.
