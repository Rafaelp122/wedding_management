## Frontend Testing — Regras Críticas (isolate: false)

- **NUNCA** use `vi.mock("@/api/generated/...", () => ({...}))` com factory síncrona.
  Causa colisão de módulos sob `isolate: false`.
- **SEMPRE** prefira MSW (`server.use(http.METHOD(url, handler))`).
- Se `vi.mock` for inevitável (controle de isPending, loading states):
  use `async (importOriginal) => ({ ...original, hookOverride: ... })`.
- Mocks globais ficam em `test-setup.ts`. Nunca per-file para deps compartilhadas.
