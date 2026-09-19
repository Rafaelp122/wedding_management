# Wedding Management - Global Engineering Context

## Tech Stack & Architecture Overview

- **Stack**: Python 3.12+ (Django Ninja) | React 19 + TypeScript + Vite + Tailwind CSS 4 + shadcn/ui.
- **Single Source of Truth (`docs/`)**: Documentation follows **Diátaxis** in `docs/`. Always consult `docs/index.md` before architectural or domain changes.
- **On-Demand Skills (`.agents/skills/`)**: Skills are task-specific operational playbooks loaded on demand (never proactively).

## Universal Guard-Rails (Non-Negotiable)

### Backend (ADR-006, ADR-011, ADR-016, ADR-030, ADR-031)

- **Rich Domain Model (Rich Active Record)**: Entidades herdam `BaseModel` / `TenantModel` e encapsulam suas invariantes, máquinas de estado (`ALLOWED_TRANSITIONS`) e métodos de ciclo de vida (`complete()`, `cancel()`, `transition_to()`). PROIBIDO modelo anêmico ou mutação procedural de estado dentro de services. O `clean()` do model é o guardião de integridade (`full_clean()` no `save()`).
- **Validação em 3 Níveis Formais (ADR-030)**:
  - _Nível 1 (Entrada / Sintaxe)_: Pydantic Schemas (`schemas.py`) tratam tipos, strings (`str_strip_whitespace=True`) e limites numéricos (Fail-Fast HTTP 422).
  - _Nível 2 (Invariantes de Domínio)_: Django Models (`models.py`) tratam regras intrínsecas, transições de estado e `clean()`.
  - _Nível 3 (Caso de Uso / Orquestração)_: Services (`services.py`) orquestram `@transaction.atomic`, multi-tenancy (`validate_tenant_ownership`), dependências entre agregados e efeitos colaterais.
- **Isolamento de Bounded Contexts & Interfaces (ADR-031)**: PROIBIDO importar `models.py`, `services.py` ou `managers.py` de outros domínios diretamente. Toda comunicação síncrona transacional entre módulos passa exclusivamente por `apps.<contexto>.interfaces`. Efeitos secundários utilizam tarefas assíncronas coordenadas (`django.tasks`) enfileiradas pós-commit (`transaction.on_commit`). Consultas analíticas compostas multi-domínio residem exclusivamente em `apps/reporting`. Toda dependência é auditada pelo `import-linter` (`just lint-imports`).
- **Service Layer & CQRS**: Rotas de mutação (`POST`, `PUT`, `PATCH`, `DELETE`) em `api.py` delegam para `services/`. Rotas `GET` delegam para `selectors/` e `managers.py` (`TenantQuerySet`), retornando querysets lazy e chainable. PROIBIDO métodos de leitura pura em `services.py`.
- **Multi-Tenancy (ADR-009, ADR-016, ADR-019)**: Todo service/selector aceita `company` e filtra via `Model.objects.for_tenant(company)`. Use `validate_tenant_ownership` em services e `get_object_or_404_for_tenant` ou `*_get_selector` para lookups individuais.
- **Data Integrity & Typing**: Modelos herdam `BaseModel` (`full_clean()` no `save()`). Tipagem estrita `mypy` obrigatória.
- **Router Endpoints**: `operation_id` obrigatório em todos os endpoints de router.
- **YAGNI & Outside-In Domain Modeling (Anti-Código Morto)**: É ESTRITAMENTE PROIBIDO criar métodos, propriedades (`@property`) ou utilitários em modelos Django de forma preventiva ou especulativa ("para o futuro"). Todo método ou propriedade adicionado a um model DEVE ter um consumidor de produção imediato e obrigatório (um Service de caso de uso, um Seletor analítico, um Schema de API Ninja ou uma invariante no `clean()`). Código coberto apenas por `test_models.py` sem chamador em produção é considerado violação de YAGNI e débito técnico.

### Frontend (ADR-012, ADR-024)

- **Padrão Smart/Dumb (ADR-024)**:
  - _Smart Components (Containers/Pages)_: Orquestram chamadas de rede (hooks Orval/TanStack Query), parâmetros de rota e formulários, repassando dados e callbacks via Props.
  - _Dumb Components (Presenters/Views)_: Puramente visuais e síncronos (Props-driven). PROIBIDO hooks diretos de mutação/query ou controle de rotas dentro de dumb components (permissão estrita apenas para importar tipos TypeScript via `import type`).
  - _Helpers Puros_: Cálculos matemáticos, agregações e manipulações de datas devem ser extraídos para funções utilitárias puras e determinísticas em `utils/` ou `helpers.ts`.
- **API Access (ADR-012)**: PROIBIDO usar `fetch` ou `axios` diretamente. Use EXCLUSIVAMENTE hooks gerados pelo Orval (`@/api/generated/`).
- **UI & Components**: Siga [DESIGN.md](DESIGN.md). Componha primitivas shadcn/ui com tokens Tailwind em `src/features/<name>/components/`. NUNCA edite arquivos em `src/components/ui/` diretamente.
- **Forms & Icons**: `react-hook-form` + `zod`. Apenas ícones da biblioteca `lucide-react`.

### Domain Business Rules (SSOT)

- **Catálogo de Regras (`docs/architecture/business-rules/`)**: Regras de negócio intrínsecas, fórmulas e máquinas de estado de finanças, logística, scheduler, casamentos e notificações residem em notas atômicas. Toda alteração de comportamento de domínio DEVE manter paridade estrita com sua respectiva nota atômica, sem doc drift.

### Testing (`isolate: false`)

- **Backend**: FORBIDDEN `.objects.create()` — use factories in `apps/*/tests/factories.py`. `services.py` requires unit success/failure coverage. `selectors/` requires unit/isolated tenant coverage in `test_selectors.py`.
- **Frontend**: FORBIDDEN `vi.mock("@/api/generated/...")` or per-file data hook mocks. Centralize all mocks in `test-setup.ts` via `registerMockHook`. Import testing utilities from `@/test-utils`.

### Documentation & Comments

- **Diátaxis & Atomic Notes**: Follow **Diátaxis** and **Atomic Notes** in `docs/` ([documentation-standards](docs/reference/architecture-standards/documentation-standards.md)). Cross-link atomic notes without text duplication. Run `just check-docs` (or `uv run --project backend python scripts/validate_docs_links.py`).
- **PT-BR & Code Comments**: Write comments/docstrings in Portuguese (PT-BR) following [commenting-standards](docs/reference/architecture-standards/commenting-standards.md). Use Google Style for public service methods.
- **No AI Mentions**: PROHIBITED to reference AI tools, assistants, or generators (e.g. "Bolt", "Jules", "Copilot") in comments or documentation.

## Subagents Dispatch Matrix

Dispatch subagents for multi-file changes, multi-step logic, or heavy investigations. Keep the main conversation thread for direct questions and coordination.

| Subagent       | Role & Trigger                                                                  |
| :------------- | :------------------------------------------------------------------------------ |
| **`backend`**  | Django models, services, endpoints, migrations, backend tests, business logic   |
| **`frontend`** | React components, pages, custom hooks, forms, Orval integration, frontend tests |
| **`design`**   | UI/UX layouts, Tailwind styling, theme tweaks, component accessibility          |
