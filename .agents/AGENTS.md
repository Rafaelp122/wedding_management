## Frontend Testing — Regras Críticas (isolate: false)

- **NUNCA** use `vi.mock("@/api/generated/...", () => ({...}))` com factory síncrona.
  Causa colisão de módulos sob `isolate: false`.
- **SEMPRE** prefira MSW (`server.use(http.METHOD(url, handler))`).
- Se `vi.mock` for inevitável (controle de isPending, loading states):
  use `async (importOriginal) => ({ ...original, hookOverride: ... })`.
- Mocks globais ficam em `test-setup.ts`. Nunca per-file para deps compartilhadas.
- FORBIDDEN `vi.mock("@/api/generated/...")` em arquivos de teste. Todo mock de hook Orval
  deve ser registrado exclusivamente em `test-setup.ts` via `registerMockHook`.

## Frontend Component Architecture — Padrão Smart/Dumb e Testabilidade

- **SEMPRE** separe componentes complexos ou de páginas em **Smart Components (Containers)** e **Dumb Components (Presenters/Views)**.
- **Smart Components**: Devem encapsular a lógica de queries e mutações (Orval/TanStack Query), leitura de parâmetros de rotas (React Router) e estados de formulários. Eles passam dados processados e callbacks simples para as Views.
- **Dumb Components**: Devem ser puramente visuais, recebendo callbacks e dados via Props. Devem ser síncronos e sem side-effects de rede ou navegação, facilitando testes unitários rápidos. É permitida a importação de tipos estáticos gerados (`import type { ... }` do Orval/API) para garantir a integridade da tipagem estrita no TypeScript.
- **Lógica Pura de Helpers**: Todo processamento matemático de gráficos, agregação de dados ou formatação complexa deve ficar em funções puras em arquivos utilitários (ex: `utils/`) para permitir testes unitários puros rápidos.
- **Mapeamento de Cache de Módulos (Imports)**: Em testes unitários sob `isolate: false`, garanta que o caminho de importação do mock no arquivo de teste (`.test.tsx`) seja idêntico ao import do componente real (ex: relative `../hooks` vs absolute `@/`). Diferenças no formato de import podem duplicar a instância do módulo no cache do Vite, fazendo com que o `vi.mocked` falhe em interceptar a chamada do componente.
