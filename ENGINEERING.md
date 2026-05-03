# Wedding Management - Engineering Context (Shared)

> **⚠️ ATENÇÃO: Este arquivo é de uso exclusivo para agentes de IA.** Ele fornece contexto técnico e regras estritas para garantir a consistência do código. Desenvolvedores humanos devem consultar a documentação em `docs/`.

This file serves as the Single Source of Truth for all AI agents and developers working on this project.

## 🚀 Tech Stack

- **Backend**: Python 3.12+, Django, Django Ninja (Strict: No DRF).
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui.
- **Tools**: Orval (Contract-driven API), Docker, Makefile, uv (Python pkg manager).
- **Infrastructure**: PostgreSQL (Neon), Cloud Run, R2 (Storage via ADR-004).

## 🏗 Architectural Rules (Strict)

### Backend (apps/)
- **Service Layer Pattern**: Endpoints in `api.py` MUST ONLY call functions in `services.py`. Lógica de negócio nunca fica na API.
- **Multi-tenancy**: Todo serviço deve explicitamente receber `company` e usar `Model.objects.for_tenant(company)` para filtragem obrigatória (ver ADR-009 e ADR-016).
- **Data Integrity**: Models herdam de `BaseModel` que executa `full_clean()` no `save()` (ver ADR-011).
- **Operations**: Sempre defina `operation_id` nos routers (ex: `weddings_list`) para geração correta do Orval.
- **Typing**: O projeto usa tipagem estática rigorosa. O `mypy` deve passar sem erros.

### Frontend (src/)
- **Feature-Based Architecture**: Organizado por features em `src/features/<feature_name>/`.
  - Estrutura: `/components`, `/hooks`, `/pages`, `/types.ts`, `/utils`.
- **shadcn/ui**:
  - Componentes de UI base residem em `src/components/ui/`.
  - Componentes de negócio residem na pasta da feature.
  - Priorize composição e Tailwind em vez de alterar arquivos da pasta `ui` diretamente.
- **API Consumption**: PROIBIDO usar `fetch` ou `axios` manualmente. Use exclusivamente hooks gerados pelo Orval em `src/api/generated/`.
- **Forms**: Use `react-hook-form` integrado com `zod` para validação.
- **Icons**: Use exclusivamente `lucide-react`.

## 🧪 Testing Standards (Mandatory)

### 🐍 Backend (Pytest)
- **Factories Over DB**: É PROIBIDO o uso de `.objects.create()` em testes. Use as classes em `backend/apps/*/tests/factories.py`.
- **Isolation**: Testes de serviço devem ser unitários/isolados. Use Factories para dados de apoio.
- **Coverage**: Toda função em `services.py` deve ter pelo menos um teste de sucesso e um de falha (exceção esperada).

### ⚛️ Frontend (Vitest & RTL)
- **User-Centric**: Teste o comportamento do usuário. Priorize queries de acessibilidade (`getByRole`, `getByLabelText`).
- **Mocking**: Mocke os hooks do Orval usando `vi.mock`. Não faça chamadas reais de API em testes.
- **Data**: Use `faker` para gerar payloads de teste e mocks de API consistentes.

## 🔄 Workflow Conventions

- **Commits**: Siga o padrão Conventional Commits (ex: `feat(weddings): add list endpoint`).
- **ADRs**: Mudanças estruturais DEVEM gerar um novo arquivo em `docs/ADR/` seguindo a numeração sequencial.
- **Lint/Format**: Execute `make lint` ou `ruff check .` antes de qualquer push. O pre-commit deve estar ativo.
- **Secrets**: Nunca commite segredos. Usamos `detect-secrets` para prevenir vazamentos.
