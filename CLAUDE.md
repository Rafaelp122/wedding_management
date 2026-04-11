# CLAUDE.md - Wedding Management Engineering Context

## Build & Test Commands

- **Backend Setup**: `make build` (Docker) ou `uv sync` (Local)
- **Run Backend Tests**: `make test` ou `pytest backend/apps/`
- **Frontend Setup**: `cd frontend && npm install`
- **Run Frontend Tests**: `cd frontend && npm test`
- **Lint/Format**: `make lint` ou `cd backend && ruff check .`
- **Generate API Client**: `make orval` ou `cd frontend && npx orval`

## Tech Stack

- **Backend**: Python 3.12+, Django, Django Ninja (Strict: No DRF).
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Shadcn UI.
- **Tools**: Orval (Contract-driven API), Docker, Makefile, uv (Python pkg manager).

## Architectural Rules (Strict)

### Backend (apps/)

- **Service Layer Pattern**: Endpoints em `api.py` devem apenas chamar funções em `services.py`.
- **Multi-tenancy**: Todo serviço deve receber explicitamente o `user=request.user` para filtragem.
- **Operations**: Sempre definir `operation_id` nos routers (ex: `weddings_list`).
- **Data Integrity**: Modelos herdam de `BaseModel` que executa `full_clean()` no `save()`.
- **Deletion**: Hard delete é o padrão. Não implementar soft delete.
- **Error Handling**: Usar `MUTATION_ERROR_RESPONSES` e `READ_ERROR_RESPONSES` do core.

### Frontend (src/)

- **Feature-Based Architecture**: Código organizado por features em `src/features/<feature_name>/`.
  - Estrutura: `/components`, `/hooks`, `/pages`, `/types.ts`, `/utils`.
- **API Consumption**: PROIBIDO usar `fetch` ou `axios` manualmente. Usar exclusivamente os hooks gerados pelo Orval em `src/api/generated/`.
- **Typing**: TypeScript rigoroso em todos os componentes e hooks.

## Workflow Conventions

- **Commits**: Seguir Conventional Commits (ex: `feat(weddings): add list endpoint`).
- **State Management**: Estado global via Zustand em `src/stores/`.
- **Style**: Seguir padrões do Ruff (Python) e ESLint (TS).

## AI Behavior

- Sê conciso e direto.
- Omite saudações e explicações de conceitos básicos.
- Fornece código em blocos Markdown com a linguagem especificada.
- Prioriza comandos do Makefile para tarefas de infraestrutura.
