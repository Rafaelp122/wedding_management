---
name: wedding-frontend-testing
description: "Frontend testing standards for Wedding Management System — Vitest, React Testing Library, MSW (Orval-generated), Playwright E2E patterns. Load when writing or reviewing frontend tests."
---

# Wedding Frontend Testing Standards

Testing standards for the Wedding Management System frontend — Vitest + React Testing Library + MSW + Playwright.

---

## 1. Tooling

`vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `msw` (Orval-generated handlers), `@faker-js/faker`, `playwright` (E2E).

---

## 2. Vitest Configuration

The project uses `isolate: false` for speed — all test files share a single Vite module graph. This means `vi.mock` calls are cached globally and module state persists across files. Two consequences:

1. **Mocks MUST be centralized** in `test-setup.ts` (see Section 3). Never mock shared dependencies per-file — use the global mock.
2. **State MUST be cleaned** in `afterEach`: `vi.clearAllMocks()`, `cleanup()`, `server.resetHandlers()`, and `useAuthStore.getState().logout()`.

```ts
// vitest.config.ts (key settings)
{
  isolate: false,          // shared module graph for speed
  clearMocks: true,        // reset vi.fn() call history before each test
  restoreMocks: true,      // restore original implementations
  environment: "happy-dom",
  css: false,
  deps: { optimizer: { web: { enabled: true, include: [...] } } },
}
```

---

## 3. Global Test Setup (`test-setup.ts`)

The setup file at `frontend/src/test-setup.ts` runs once before all tests. It provides:

### 3.1 Centralized Sonner Mock

`sonner` is mocked globally — **no per-file mocking needed**. Tests import `toast` directly and assert on it:

```ts
// test-setup.ts (global, already in place)
const globalAny = globalThis as any;
if (!globalAny.__SONNER_MOCK__) {
  globalAny.__SONNER_MOCK__ = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
    loading: vi.fn(),
    dismiss: vi.fn(),
    custom: vi.fn(),
  };
}
vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return { ...actual, toast: globalAny.__SONNER_MOCK__ };
});
```

```tsx
// ✅ In tests — import toast directly, no per-file mock
import { toast } from "sonner";

expect(toast.success).toHaveBeenCalledWith("Conta criada com sucesso!");
expect(toast.error).toHaveBeenCalled();
```

### 3.2 Centralized Sentry Mock

```ts
vi.mock("@sentry/react", () => ({
  setContext: vi.fn(),
  captureException: vi.fn(),
}));
```

### 3.3 MSW Server

```ts
import { server } from "@/mocks/server";
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### 3.4 DOM Patches

- **Happy-dom submit workaround**: Patches `HTMLElement.prototype.dispatchEvent` so `userEvent.click()` on submit buttons triggers `form.dispatchEvent(new Event("submit"))`.
- **matchMedia**: Stubbed with `vi.fn()` returning `{ matches: false, media, ... }`.
- **ResizeObserver**: Stubbed with no-op `{ observe, unobserve, disconnect }`.

### 3.5 Cleanup (`afterEach`)

```ts
afterEach(() => {
  cleanup();                              // unmount React trees
  server.resetHandlers();                 // reset MSW overrides
  vi.clearAllMocks();                     // reset all vi.fn() history
  document.body.removeAttribute("data-scroll-locked");
  document.body.style.pointerEvents = "";
  document.documentElement.style.pointerEvents = "";
  useAuthStore.getState().logout();       // reset auth state
});
```

---

## 4. Custom Render Wrapper (`test-utils.tsx`)

The project provides its own `render` and `renderHook` that wrap components with required providers:

```tsx
// test-utils.tsx — wraps every render with:
<QueryClientProvider client={queryClient}>
  <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
    <RouterProvider router={router} />
    <Toaster />   {/* enables sonner toast rendering */}
  </ThemeProvider>
</QueryClientProvider>
```

**Always import from `@/test-utils`**, never from `@testing-library/react` directly:

```tsx
// ✅ CORRECT
import { render, screen, userEvent, waitFor } from "@/test-utils";

// ❌ WRONG — misses providers (Toaster, QueryClient, Router, Theme)
import { render, screen } from "@testing-library/react";
```

The custom `userEvent` export has `pointerEventsCheck: 0` by default — no need to configure it per test.

```tsx
import { userEvent } from "@/test-utils";
const user = userEvent.setup();
```

---

## 5. API Mocking — Two Layers

The project uses two complementary strategies:

### 5.1 MSW (Mock Service Worker) — Integration Tests

Orval auto-generates MSW handlers in `src/api/generated/v1/endpoints/*/*.msw.ts`. Global setup:

```ts
// frontend/src/mocks/server.ts
import { setupServer } from "msw/node";

// frontend/src/mocks/handlers.ts
import { getAuthMock } from "@/api/generated/v1/endpoints/auth/auth.msw";
import { getWeddingsMock } from "@/api/generated/v1/endpoints/weddings/weddings.msw";
// ... all domains

export const handlers = [
  ...getAuthMock(),
  ...getWeddingsMock(),
  ...getFinancesMock(),
  ...getLogisticsMock(),
  ...getSchedulerMock(),
  ...getDashboardMock(),
];
```

**When to use MSW**: Integration tests where the component makes real requests (via Orval hooks) and you want to test the full request → response → render flow.

**Handler override for error scenarios**:
```ts
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

test("shows error on API failure", async () => {
  server.use(
    http.get("/api/weddings", () =>
      HttpResponse.json({ error: "Server error" }, { status: 500 })
    )
  );
  // render component, assert error state
});
```

### 5.2 MSW (Mock Service Worker) — Padrão Preferido

O projeto usa MSW como padrão para mockar APIs em testes de unidade.  
NUNCA use `vi.mock` com factory síncrona `() => ({})` em módulos Orval gerados — isso apaga o módulo inteiro e causa colisões com `isolate: false`.

```ts
// ❌ PROIBIDO — factory síncrona apaga o módulo inteiro com isolate:false
vi.mock("@/api/generated/v1/endpoints/logistics/logistics", () => ({
  useLogisticsItemsUpdate: () => ({ mutate: vi.fn(), isPending: false }),
}));

// ✅ PREFERIDO — MSW, sem risco de colisão
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

server.use(
  http.patch("/api/v1/logistics/items/:uuid", async ({ request, params }) => {
    const body = await request.json();
    return HttpResponse.json(createMockItem({ uuid: params.uuid as string, ...body }));
  })
);
```

**Quando usar `vi.mock`** (única exceção): para simular `isLoading: true` em testes de loading state.  
Nesse caso, SEMPRE use `importOriginal` para preservar as outras exports:

```ts
vi.mock("@/api/generated/v1/endpoints/weddings/weddings", async (importOriginal) => {
  const original = await importOriginal<typeof import("...")>();
  return { ...original, useWeddingsRetrieve: () => ({ data: undefined, isLoading: true, isError: false }) };
});
```

### 5.3 Regra de Ouro — vi.mock em Módulos Orval

1. NUNCA use `vi.mock("@/api/generated/...", () => ({...}))` — factory síncrona.
2. SEMPRE prefira MSW (`server.use(http.METHOD(url, handler))`).
3. Se `vi.mock` for inevitável (ex: loading state), use `async (importOriginal) => ({ ...original, hookOverride: ... })`.
4. Mocks globais ficam em `test-setup.ts`. Nunca per-file para deps compartilhadas.

### Summary: which to use?

| Scenario | Strategy |
|----------|----------|
| Page/flow integration test | MSW (let hooks call the "network") |
| Isolated component unit test | `vi.mock` (mock hook directly) |
| Loading/empty state test | `vi.mock` (simpler to control) |
| API error test | MSW `server.use()` with error status |

---

## 6. React Testing Library — Patterns

### Queries (accessibility priority)

```tsx
// ✅ CORRECT — accessibility queries
const button = screen.getByRole("button", { name: /create/i });
const input = screen.getByLabelText(/name/i);
const heading = screen.getByRole("heading", { name: /weddings/i });

// ✅ For async operations
const item = await screen.findByText(/loaded/i);
await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());
```

### User Event (always use `userEvent`, never `fireEvent`)

```tsx
import { userEvent } from "@/test-utils";

const user = userEvent.setup();
await user.click(button);
await user.type(input, "text");
await user.clear(input);
await user.selectOptions(select, "option");
```

---

## 7. Testing Forms (react-hook-form + zod)

```tsx
test("submits form with valid data", async () => {
  const onSubmit = vi.fn();
  render(<WeddingForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText(/bride name/i), "Maria");
  await user.type(screen.getByLabelText(/date/i), "2026-12-25");
  await user.click(screen.getByRole("button", { name: /save/i }));

  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ bride_name: "Maria" })
    );
  });
});

test("shows validation errors", async () => {
  render(<WeddingForm onSubmit={vi.fn()} />);
  await user.click(screen.getByRole("button", { name: /save/i }));

  expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
});
```

---

## 8. Testing shadcn/ui Components

### Portal queries

Components like `Dialog`, `Sheet`, `DropdownMenu` render in Radix portals — outside the default RTL container.

```tsx
// For queries on portal-rendered components:
const dialogContent = within(screen.getByRole("dialog"));
expect(dialogContent.getByText(/confirm/i)).toBeInTheDocument();

// Or use baseElement to search outside the container:
const { baseElement } = render(<MyPage />);
expect(within(baseElement).getByRole("dialog")).toBeInTheDocument();
```

### Radix Dialog — Accessibility Requirement

`DialogContent` **requires** both `<DialogTitle>` and `<DialogDescription>` for screen reader accessibility. This applies to **every state** rendered inside a `DialogContent`, including loading, error, and empty states.

Use `className="sr-only"` to hide them visually while satisfying the requirement:

```tsx
{isLoading ? (
  <>
    <DialogTitle className="sr-only">Carregando fornecedor...</DialogTitle>
    <DialogDescription className="sr-only">Carregando fornecedor...</DialogDescription>
    <div className="space-y-3 py-4">
      <Skeleton className="h-6 w-48" />
      <Skeleton className="h-4 w-32" />
    </div>
  </>
) : error ? (
  <>
    <DialogTitle className="sr-only">Erro ao carregar</DialogTitle>
    <DialogDescription className="sr-only">Erro ao carregar</DialogDescription>
    <Alert variant="destructive">...</Alert>
  </>
) : !data ? (
  <>
    <DialogTitle className="sr-only">Não encontrado</DialogTitle>
    <DialogDescription className="sr-only">Não encontrado</DialogDescription>
    <Alert>...</Alert>
  </>
) : (
  <DialogHeader>
    <DialogTitle>{data.name}</DialogTitle>
    <DialogDescription>Detalhes do item</DialogDescription>
  </DialogHeader>
)}
```

**Rule**: Every branch inside `DialogContent` must render a `DialogTitle` + `DialogDescription` pair. The project uses Tailwind's `sr-only` (not `@radix-ui/react-visually-hidden`).

---

## 9. Testing Charts / Recharts

jsdom has no CSS layout engine — `getBoundingClientRect()` returns `{ width: 0, height: 0 }`. Recharts' `ResponsiveContainer` reads these dimensions and emits `"width(0) and height(0)"` warnings.

**Solution**: Mock `recharts` entirely with simple `<div>` elements. This eliminates the warning and makes tests faster.

```tsx
vi.mock("recharts", () => ({
  ResponsiveContainer: ({
    children,
    width,
    height,
  }: {
    children: React.ReactNode;
    width?: string | number;
    height?: string | number;
  }) => <div data-testid="recharts-container" style={{ width, height }}>{children}</div>,
  BarChart: ({
    children,
    data,
  }: {
    children: React.ReactNode;
    data: unknown[];
  }) => <div data-testid="bar-chart" data-items={data.length}>{children}</div>,
  Bar: ({ dataKey, name }: { dataKey: string; name?: string }) => (
    <div data-testid={`bar-${dataKey}`}>{name}</div>
  ),
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  XAxis: ({ dataKey }: { dataKey: string }) => (
    <div data-testid="x-axis" data-datakey={dataKey} />
  ),
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  Cell: () => <></>,
  ReferenceLine: () => <div data-testid="reference-line" />,
}));
```

**Use `data-testid` and `data-*` attributes** on mocked elements to assert chart content:

```ts
expect(screen.getByTestId("bar-chart").dataset.items).toBe("5");
expect(screen.getByTestId("bar-amount")).toBeInTheDocument();
expect(screen.queryByTestId("cartesian-grid")).toBeInTheDocument();
```

**When to mock Recharts**: Any test file that renders a component containing `ResponsiveContainer`, `BarChart`, `LineChart`, `PieChart`, etc. The canonical example is `FinancesDistributionChart.test.tsx`.

---

## 10. Testing Zustand Stores

```tsx
import { useAuthStore } from "@/stores/auth-store";
import { act } from "@testing-library/react";

test("auth store login/logout", () => {
  const { result } = renderHook(() => useAuthStore());

  act(() => {
    result.current.setUser({ id: "1", name: "Test" });
  });

  expect(result.current.user).toEqual({ id: "1", name: "Test" });

  act(() => {
    result.current.logout();
  });

  expect(result.current.user).toBeNull();
});
```

---

## 11. Playwright — E2E Testing

### Structure

```
frontend/e2e/
├── fixtures.ts           # Auth setup, test data
├── pages/                # Page Object Models
│   ├── login.page.ts
│   └── weddings.page.ts
└── tests/
    ├── auth.spec.ts
    └── weddings.spec.ts
```

### Essential Patterns

```ts
// Page Object Model
export class WeddingsPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/app/weddings");
  }

  async createWedding(data: { bride: string; date: string }) {
    await this.page.getByRole("button", { name: /create/i }).click();
    await this.page.getByLabel(/bride/i).fill(data.bride);
    await this.page.getByRole("button", { name: /save/i }).click();
  }
}
```

### Locators (priority order)

```ts
// 1. Role-based (accessibility)
page.getByRole("button", { name: /create/i });
page.getByLabel(/name/i);

// 2. Text content
page.getByText(/active weddings/i);

// 3. Test ID (last resort)
page.getByTestId("wedding-card");
```

### Authentication in Tests

```ts
// fixtures.ts — reuse authenticated state
export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("test@example.com");
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL("/app/dashboard");
    await use(page);
  },
});
```

### Flaky Test Prevention

- Use `waitForResponse` or `waitForURL` instead of `page.waitForTimeout`
- Prefer `expect(...).toBeVisible()` over fixed timeouts
- Isolate tests: each `.spec.ts` should clean state or use fresh fixtures

---

## 12. References

For complete tooling APIs, load these skills:

| Tool | Skill | Content |
|------|-------|---------|
| Vitest CLI, expect, vi, hooks, coverage | `vitest` | Full Vitest API reference |
| Playwright locators, POM, flaky tests, CI | `playwright-best-practices` | Complete Playwright E2E guide |
| Frontend architecture conventions | `wedding-frontend` | Feature-based, Orval, forms, icons |
