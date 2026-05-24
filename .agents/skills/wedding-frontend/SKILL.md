---
name: wedding-frontend
description: "Frontend architecture and conventions for Wedding Management System — feature-based structure, Orval hooks, react-hook-form + zod, lucide-react icons, Zustand stores, shadcn/ui composition, routing. Load when building UI components, pages, or forms."
---

# Wedding Management Frontend

React 19 + TypeScript + Vite 7 + Tailwind CSS 4 + shadcn/ui.

---

## 1. Feature-Based Architecture

```
src/features/<feature_name>/
├── components/     # Feature-specific components
├── hooks/          # Feature-specific hooks
├── pages/          # Pages (lazy-loaded)
├── types.ts        # Feature types
└── utils.ts        # Utilities
```

---

## 2. Routing

- Public routes (landing, login): `PublicLayout` + `PublicRoute` guard
- Protected routes (dashboard, weddings, etc.): `/app` prefix, `AppLayout` inside `ProtectedRoute`
- ALL routes are lazy-loaded with `React.lazy` + `Suspense`

---

## 3. API Consumption (CRITICAL)

`FORBIDDEN: fetch` or manual `axios`. Use only Orval-generated hooks.

```tsx
// ✅ CORRECT
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings";
const { data } = useWeddingsList();

// ✅ CORRECT — mutation
import { useWeddingsCreate } from "@/api/generated/v1/endpoints/weddings";
const { mutate } = useWeddingsCreate();

// ❌ WRONG — NEVER do this
const res = await fetch("/api/weddings");
const res = await axios.get("/api/weddings");
```

- Hooks: `src/api/generated/v1/endpoints/`
- Zod schemas: `src/api/generated/v1/zod/`
- After API changes: `make orval`

---

## 4. Forms

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const formSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email"),
});

type FormValues = z.infer<typeof formSchema>;

function MyForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
  });
  // ...
}
```

- Always use `react-hook-form` + `zod` + `@hookform/resolvers`
- Client-side validation via Zod schema
- Orval schemas available in `src/api/generated/v1/zod/`

---

## 5. Icons

Only `lucide-react`:

```tsx
import { Plus, Pencil, Trash2, Search } from "lucide-react";

<Button><Plus className="mr-2 h-4 w-4" /> Create</Button>
```

---

## 6. UI Components (shadcn/ui)

- Base components in `src/components/ui/`
- `NEVER` edit files directly in the `ui/` folder
- Prefer composition with Tailwind:

```tsx
// ✅ CORRECT — compose with className
<Card className="border-dashed bg-muted/50">
  <CardHeader>
    <CardTitle className="text-lg">Title</CardTitle>
  </CardHeader>
</Card>

// ❌ WRONG — editing the original Card file
```

---

## 7. State Management

### Zustand (global)

```tsx
// src/stores/auth-store.ts
import { create } from "zustand";

interface AuthState {
  user: User | null;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
```

### TanStack Query (server state)

```tsx
import { useQueryClient } from "@tanstack/react-query";

// Invalidation after mutation
const queryClient = useQueryClient();
queryClient.invalidateQueries({ queryKey: ["weddings"] });
```

---

## 8. Tailwind CSS 4

- Use utility classes directly in JSX
- Colors and themes via shadcn/ui CSS variables
- `NEVER` use inline CSS (`style={{}}`) or separate CSS modules

```tsx
// ✅ CORRECT
<div className="flex items-center gap-4 p-6 bg-background rounded-lg border">

// ❌ WRONG
<div style={{ display: "flex", padding: "24px" }}>
```

---

## 9. Anti-Patterns

| Anti-pattern | Fix |
|-------------|-----|
| Manual `fetch()` or `axios()` | Corresponding Orval hook |
| Icon from another lib (`@mui/icons`, `react-icons`) | `lucide-react` |
| Editing `src/components/ui/button.tsx` | Compose with Tailwind in the parent component |
| Form with `useState` per field | `react-hook-form` + `zod` |
| Inline CSS (`style={{}}`) | Tailwind utility classes |
| Component without lazy load in route | `React.lazy(() => import(...))` |

---

## 10. Commands

```bash
cd frontend && npm test                   # Tests
cd frontend && npm run lint               # Lint + typecheck
make orval                                # Regenerate hooks after API changes
docker compose exec frontend npm test     # Via Docker
```

---

## 11. Clean Code — TypeScript/React

### Naming
- **TypeScript/React**: Use `camelCase` for variables, functions, custom hooks. Use `PascalCase` for components, types, interfaces, classes.
- Avoid generic names like `d` or `data`. Use `supplierList` or `isLoading`.
- **Method names**: Verbs for actions (`getSupplier`, `createWedding`), nouns for types/interfaces.

### Components & Hooks (SRP)
- Components: keep JSX presentation simple. Extract complex state, effects, or API queries into custom hooks.
- Custom hooks: manage one main concern (e.g. pagination state OR modal state, not both).
- Pure functions preferred — no direct mutation of React state (use immutable updates).

### ORM & DTOs (Orval)
- Functional JS array methods (`.filter().map()`) are idiomatic and encouraged — not a Law of Demeter violation.
- TypeScript DTOs: use `interface` or `type`, mainly generated by Orval. No business logic inside these structures.

### Error Handling & Null Safety
- `null`/`undefined` is acceptable for representing absent data — always type it explicitly (`User | null`).
- Use optional chaining (`user?.profile?.avatar`). Let TypeScript compiler enforce null-checks.

### Comments
- Prefer self-explanatory code over comments.
- Keep comments only for: complex business rules, browser/DB workarounds, `TODO` notes.
- Never: comments that repeat what the code obviously does.
