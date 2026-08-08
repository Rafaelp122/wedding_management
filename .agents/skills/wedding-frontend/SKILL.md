---
name: wedding-frontend
description: "Frontend architecture and conventions for Wedding Management System — feature-based structure, Orval hooks, react-hook-form + zod, lucide-react icons, Zustand stores, shadcn/ui composition, routing. Load when building UI components, pages, or forms."
---

# Wedding Frontend Playbook

Operational guide and checklist for React 19 + TypeScript + Vite + Tailwind CSS v4 frontend development.

## Documentation References

- **Smart/Dumb Architecture**: [smart-dumb-components.md](../../../docs/4-explanation/architecture/smart-dumb-components.md)
- **UI Design System**: [DESIGN.md](../../../DESIGN.md)
- **UI Components Spec**: [ui-components-spec.md](../../../docs/3-reference/frontend/ui-components-spec.md)
- **Orval Code Generation**: [generate-orval-client.md](../../../docs/2-how-to/frontend/generate-orval-client.md)

## Development Checklist

### 1. Feature Structure & Smart/Dumb Pattern
- Place code in `src/features/<feature_name>/` (`components/`, `hooks/`, `pages/`, `types.ts`, `utils.ts`).
- Separate Smart Components (containers: API queries, routes, form state) from Dumb Components (presenters: pure UI, props only). See [smart-dumb-components.md](../../../docs/4-explanation/architecture/smart-dumb-components.md).

### 2. API Integration (Strict Rule)
- **FORBIDDEN**: `fetch()` or `axios`. Use ONLY Orval-generated hooks in `@/api/generated/v1/endpoints/`.
- Regenerate hooks after backend changes using `make orval`. See [generate-orval-client.md](../../../docs/2-how-to/frontend/generate-orval-client.md).

### 3. Forms & Validation
- Always use `react-hook-form` with `zod` schema validation via `@hookform/resolvers/zod`.
- Import or extend Zod schemas from `src/api/generated/v1/zod/`.

### 4. Icons & UI Composition (shadcn/ui + Tailwind v4)
- **Icons**: Use ONLY `lucide-react`. Never import from other icon libraries.
- **shadcn/ui**: Base components reside in `src/components/ui/`. NEVER modify files inside `ui/` directly.
- **Composition**: Customize styling by composing shadcn components with Tailwind CSS v4 utility classes. Avoid inline `style={{}}` and CSS modules. Follow design rules in [DESIGN.md](../../../DESIGN.md) and [ui-components-spec.md](../../../docs/3-reference/frontend/ui-components-spec.md).

### 5. State Management & Routing
- **Global Client State**: Use Zustand (`src/stores/`).
- **Server State**: Managed via Orval TanStack Query hooks. Invalidate via `queryClient.invalidateQueries()`.
- **Routing**: Public routes use `PublicLayout`/`PublicRoute`. Protected routes use `/app` prefix with `AppLayout`. Core workflow routes static; secondary/admin routes lazy-loaded (`React.lazy` + `Suspense`).

### 6. Verification
- `cd frontend && npm run lint` (Lint + Typecheck)
- `cd frontend && npm test` (Vitest suite)