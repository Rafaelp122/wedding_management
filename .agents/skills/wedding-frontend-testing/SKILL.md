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

## 2. API Mocking — Two Layers

The project uses two complementary strategies:

### 2.1 MSW (Mock Service Worker) — Integration Tests

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

// frontend/src/setupTests.ts
import { server } from "./mocks/server";
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
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

### 2.2 `vi.mock` — Component Unit Tests

For component unit tests, mock Orval hooks directly:

```tsx
// ✅ CORRECT — mock Orval hooks, NEVER make real API calls
vi.mock("@/api/generated/v1/endpoints/weddings");
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings";
vi.mocked(useWeddingsList).mockReturnValue({
  data: mockWeddings,
  isLoading: false,
});
```

**When to use `vi.mock`**: Component unit tests where you want precise control over hook return values without going through MSW.

### Summary: which to use?

| Scenario | Strategy |
|----------|----------|
| Page/flow integration test | MSW (let hooks call the "network") |
| Isolated component unit test | `vi.mock` (mock hook directly) |
| Loading/empty state test | `vi.mock` (simpler to control) |
| API error test | MSW `server.use()` with error status |

---

## 3. React Testing Library — Patterns

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
import userEvent from "@testing-library/user-event";

const user = userEvent.setup();
await user.click(button);
await user.type(input, "text");
await user.clear(input);
await user.selectOptions(select, "option");
```

---

## 4. Testing Forms (react-hook-form + zod)

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

## 5. Testing shadcn/ui Components

Components like `Dialog`, `Sheet`, `DropdownMenu` render in Radix portals — outside the default RTL container.

```tsx
// For queries on portal-rendered components:
const dialogContent = within(screen.getByRole("dialog"));
expect(dialogContent.getByText(/confirm/i)).toBeInTheDocument();

// Or use baseElement to search outside the container:
const { baseElement } = render(<MyPage />);
// query inside the portal
expect(within(baseElement).getByRole("dialog")).toBeInTheDocument();
```

---

## 6. Testing Zustand Stores

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

## 7. Playwright — E2E Testing

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

## 8. References

For complete tooling APIs, load these skills:

| Tool | Skill | Content |
|------|-------|---------|
| Vitest CLI, expect, vi, hooks, coverage | `vitest` | Full Vitest API reference |
| Playwright locators, POM, flaky tests, CI | `playwright-best-practices` | Complete Playwright E2E guide |
| Frontend architecture conventions | `wedding-frontend` | Feature-based, Orval, forms, icons |
