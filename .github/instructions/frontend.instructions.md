---
applyTo: "frontend/src/**/*.{ts,tsx}"
---

# Frontend Specific Instructions

- **Feature-based**: Files go in `src/features/<name>/` with `/components`, `/hooks`, `/pages`, `/types.ts`, `/utils`.
- **API**: FORBIDDEN `fetch`/`axios`. Use only Orval hooks from `src/api/generated/`.
- **shadcn/ui**: Base components in `src/components/ui/`. Business components in feature folder. Compose, don't modify ui/ files.
- **Forms**: `react-hook-form` + `zod` schemas from `src/api/generated/v1/zod/`.
- **Icons**: `lucide-react` only.
- **State**: Zustand stores in `src/stores/` for global state. Local state preferred for UI-only.
- **Tests**: Import `render`/`screen`/`userEvent` from `@/test-utils` (never from `@testing-library/react`). Mock Orval hooks with `vi.mock`.
- **Typing**: Avoid `any`. Use Orval-generated types from `src/api/generated/v1/models/`.
