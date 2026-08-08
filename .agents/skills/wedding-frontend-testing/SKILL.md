---
name: wedding-frontend-testing
description: "Frontend testing standards for Wedding Management System — Vitest, React Testing Library, MSW (Orval-generated), Playwright E2E patterns. Load when writing or reviewing frontend tests."
---

# Wedding Frontend Testing Playbook

Operational testing checklist for Vitest, React Testing Library, MSW, and Playwright E2E.

## Documentation References

- **Testing Architecture & Standards**: [testing-standards.md](../../../docs/3-reference/architecture-standards/testing-standards.md)
- **MSW & RTL Testing Patterns**: [msw-testing-patterns.md](../../../docs/2-how-to/frontend/msw-testing-patterns.md)
- **Playwright E2E Testing**: [run-playwright-e2e.md](../../../docs/2-how-to/frontend/run-playwright-e2e.md)

## Testing Checklist

### 1. Module Isolation (`isolate: false`)
- Vitest runs with `isolate: false` for performance. Shared module state across tests.
- Centralize shared mocks in `src/test-setup.ts`. Clean state in `afterEach`.

### 2. Imports & Test Utilities (Strict Rule)
- **ALWAYS** import `render`, `screen`, `userEvent`, `waitFor` from `@/test-utils` (never directly from `@testing-library/react`).
- `@/test-utils` injects required providers (`QueryClientProvider`, `ThemeProvider`, `RouterProvider`, `Toaster`).

### 3. API Mocking Rules
- **FORBIDDEN**: `vi.mock("@/api/generated/...")` inside individual test files. Register mock hooks in `test-setup.ts` via `registerMockHook` to avoid module duplication under `isolate: false`.
- **PREFERRED**: Use MSW (`server.use(http.METHOD(...))`) for API integration testing. See [msw-testing-patterns.md](../../../docs/2-how-to/frontend/msw-testing-patterns.md).

### 4. Global Mocks & Special Components
- **Sonner Toast**: Globally mocked in `test-setup.ts`. Import `toast` directly from `sonner` and assert call history. NEVER add per-file `vi.mock("sonner")`.
- **Recharts**: Mock `recharts` components with simple `<div>` elements using `data-testid` to prevent jsdom zero-width/height warnings.
- **Dialog Accessibility**: Every branch rendered in `DialogContent` MUST include `DialogTitle` and `DialogDescription` (use `className="sr-only"` for loading/error/empty states).

### 5. Queries & User Interactions
- Prioritize accessible queries: `getByRole`, `getByLabelText`, `findByText`.
- Use `userEvent` from `@/test-utils` (never `fireEvent`).

### 6. E2E Testing (Playwright)
- Follow Page Object Model (POM) and fixture patterns. See [run-playwright-e2e.md](../../../docs/2-how-to/frontend/run-playwright-e2e.md).

### 7. Verification Commands
- `cd frontend && npm test` (Unit & Integration tests)
- `cd frontend && npx playwright test` (E2E tests)
