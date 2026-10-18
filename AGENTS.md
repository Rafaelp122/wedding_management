# Wedding Management — Guia do Desenvolvedor e Agente de IA (AGENTS.md)

Este documento contém as instruções mandatórias, padrões arquiteturais e guard-rails universais para qualquer agente de IA ou desenvolvedor atuando neste repositório.

---

## 1. Comandos e Tooling

* **Gerenciadores de Pacotes:** `uv` no backend (Python 3.12+) e `pnpm` no frontend/landing (React 19 / Astro). Nunca use `pip install` ou `npm install` solto.
* **Automação via `justfile`:** Sempre utilize os comandos do `justfile`:
  * `just up` — Inicia os containers essenciais (`db` e `backend`) e aplica migrações.
  * `just dev` — Inicia os containers e acompanha os logs em tempo real.
  * `just down` / `just clean` — Para containers ou limpa volumes e imagens órfãs.
  * `just db-reset` — Reseta e recria o banco de dados do zero.
  * `just migrate` / `just makemigrations` — Aplica ou gera migrações no Django ORM.
  * `just test` / `just test-cov` — Executa os testes do backend com Pytest (e relatório de cobertura).
  * `just frontend-test` — Executa os testes unitários do frontend com Vitest (`isolate: false`).
  * `just lint` / `just format` — Executa o linter e o formatador Ruff no backend.
  * `just mypy` — Valida a tipagem estática estrita do backend com Mypy.
  * `just arch` (ou `just lint-imports`) — Valida as fronteiras modulares e Bounded Contexts com `tach check`.
  * `just scaffold-module <nome>` (ou `just scaffold-app <nome>`) — Cria esqueleto físico canônico de Bounded Context (Zero Slop) e registra de forma idempotente no `tach.toml`.
  * `just sync-api` — Sincroniza contratos: exporta `openapi.json` do backend e regera os hooks tipados do Orval no frontend.
  * `just check-backend` — Executa todos os checks de qualidade do backend (`lint`, `mypy`, `arch`, `test`, `openapi`).
  * `just check-frontend` — Executa todos os checks do frontend (`lint`, `type-check`, `test`, `build`).
  * `just check-docs` — Valida links de documentação, snippets, versões e executa build estrito do MkDocs.
  * `just check-ci` — Portão de qualidade completo de CI local (`docs`, `backend`, `frontend`, `landing`).
  * `just docs-dev` / `just docs-build` — Inicia o servidor local do MkDocs ou compila a versão estrita.

---

## 2. Princípios Arquiteturais Pétreos

### 2.1 Rich Active Record & Anti-Código Morto (ADR-006, ADR-011)
* Entidades herdam `BaseModel` / `TenantModel` e encapsulam suas invariantes de domínio, máquinas de estado (`ALLOWED_TRANSITIONS`) e métodos de ciclo de vida (`complete()`, `cancel()`, etc.).
* O método `clean()` do model é o guardião de integridade (`full_clean()` no `save()`). É terminantemente proibido modelo anêmico ou mutação procedural de estado dentro de services.
* **YAGNI & Outside-In Domain Modeling:** É estritamente proibido criar métodos, propriedades (`@property`) ou utilitários em modelos Django de forma preventiva ou especulativa ("para o futuro"). Todo método ou propriedade adicionado a um model DEVE ter um consumidor de produção imediato e obrigatório (um Service de caso de uso, um Seletor analítico, um Schema de API Ninja ou uma invariante no `clean()`). Código coberto apenas por `test_models.py` sem chamador em produção é considerado violação de YAGNI e débito técnico.

### 2.2 Validação em 3 Níveis Formais (ADR-030)
* **Nível 1 (Entrada / Sintaxe):** Pydantic Schemas (`schemas.py`) tratam tipos, strings (`str_strip_whitespace=True`) e limites numéricos (Fail-Fast HTTP 422).
* **Nível 2 (Invariantes de Domínio):** Django Models (`models.py`) tratam regras intrínsecas, transições de estado e `clean()`.
* **Nível 3 (Caso de Uso / Orquestração):** Services (`services.py`) orquestram `@transaction.atomic`, multi-tenancy (`validate_tenant_ownership`), dependências inter-agregados e efeitos colaterais.

### 2.3 Isolamento de Bounded Contexts & Interfaces (ADR-031)
* Os domínios em `apps/*` são isolados e fechados. É **proibido** importar `models.py`, `services.py` ou `managers.py` de outros domínios diretamente.
* Toda comunicação síncrona transacional entre módulos passa exclusivamente por `apps.<contexto>.interfaces`.
* Efeitos secundários desacoplados utilizam tarefas assíncronas coordenadas (`django.tasks` / Huey) enfileiradas pós-commit (`transaction.on_commit`).
* Consultas analíticas compostas multi-domínio residem exclusivamente em `apps/reporting`.
* Toda fronteira de dependência é auditada e bloqueada pelo `tach check` (`just arch`).

### 2.4 Service Layer & CQRS
* Rotas de mutação (`POST`, `PUT`, `PATCH`, `DELETE`) em `api.py` delegam para `services/`.
* Rotas `GET` delegam para `selectors/` e `managers.py` (`TenantQuerySet`), retornando querysets lazy e chainable.
* Proibido métodos de leitura pura em `services.py` e proibido mutações dentro de `selectors/`.
* `operation_id` é obrigatório em todos os endpoints de router.

### 2.5 Multi-Tenancy Estrito (ADR-009, ADR-016, ADR-019)
* Todo service/selector aceita obrigatoriamente a empresa locatária (`company: Company`) e filtra via `Model.objects.for_tenant(company)`.
* Utilize `validate_tenant_ownership` em services e `get_object_or_404_for_tenant` ou `*_get_selector` para lookups individuais.

### 2.6 Frontend: Padrão Smart/Dumb & Contratos Orval (ADR-012, ADR-024)
* **Smart Components (Pages/Containers):** Orquestram chamadas de rede (hooks Orval/TanStack Query), parâmetros de rota e formulários, repassando dados e callbacks via props.
* **Dumb Components (Views/Presenters):** Puramente visuais e síncronos (Props-driven). Proibido hooks diretos de mutação/query ou controle de rotas dentro de dumb components (apenas tipos TypeScript via `import type`).
* **API Access:** Proibido usar `fetch` ou `axios` diretamente. Use EXCLUSIVAMENTE hooks gerados pelo Orval (`@/api/generated/`). Execute `just sync-api` após alterar rotas no backend.
* **UI & Estilização:** Siga [DESIGN.md](DESIGN.md). Componha primitivas shadcn/ui com Tailwind CSS 4 em `src/features/<name>/components/`. NUNCA edite arquivos em `src/components/ui/` diretamente.
* **Formulários e Ícones:** `react-hook-form` + `zod`. Apenas ícones da biblioteca `lucide-react`.

### 2.7 Governança de Documentação Diátaxis (MkDocs-First & Hubs de Domínio)
* A documentação segue o padrão **Diátaxis** em `docs/`. O `mkdocs.yml` é a Única Fonte da Verdade para navegação (proibidos MOCs burocráticos intermediários).
* Hubs de Domínio residem em `docs/architecture/domains/` e regras de negócio atômicas em `docs/architecture/business-rules/`.
* Rastreabilidade bidirecional: código aponta para o documento (`Regra de Negócio: BR-XXX (docs/...)`) e documento aponta para os símbolos de código. Links e snippets são auditados via `just check-docs`. Proibido colar código >5 linhas na doc.

### 2.8 Clean Code para Agentes de IA & Navegabilidade Semântica
* **Nomes Únicos e 'Greppáveis' (<5 matches no `rg`):** Símbolos públicos (classes, métodos de serviço, interfaces, exceptions) devem ter nomes distintivos e rastreáveis. Proibido nomes genéricos como `data`, `handler`, `Manager`, `process()`, `execute()`.
* **Exceções com Contexto do Valor Ofensivo (*Offending Value + Expected Shape*):** Exceções de domínio (`BusinessRuleViolation`, `DomainIntegrityError`, etc.) e validações devem sempre interpolar o valor recebido e o valor esperado (ex.: `raise BusinessRuleViolation(f"Status '{status}' inválido para transição; esperados: {sorted(ALLOWED_TRANSITIONS)}")`), garantindo diagnóstico instantâneo no log.
* **Early Returns e Aninhamento Raso (Max 2 níveis):** Guard clauses imediatas no topo de funções e métodos. Proibido aninhamento profundo (`if/else` encadeados dentro de loops). Limite máximo de 2 níveis de estruturas de controle.
* **Funções Curtas e Arquivos Pequenos:** Funções com 4 a 20 linhas e arquivos idealmente abaixo de 300-500 linhas, permitindo processamento em tool call única com atenção cheia.
* **Lean Provenance Docstrings (WHY, not WHAT):** Docstrings atômicas de 3 a 5 linhas em métodos públicos de services e interfaces:
  - 1 linha de resumo de negócio;
  - `Regra de Negócio:` ou `Decisão Arquitetural:` com link Markdown relativo para `docs/`;
  - `Efeitos Colaterais:` (mutações atômicas, eventos no scheduler, tasks assíncronas);
  - `Raises:` com as exceções de domínio;
  - Proibido duplicar tipos já expressos na assinatura (`Args: foo (int):`). Seção `Returns:` dispensável quando a assinatura já possui retorno tipado explícito.
* **Zero Menções a IA:** Terminantemente proibido incluir marcas ou menções a ferramentas de IA ("Bolt", "Jules", "Copilot", "gerado por IA") em comentários ou código (auditado por `test_commenting_standards.py`).

### 2.9 Padrões de Testes (`isolate: false`)
* **Backend:** Proibido `.objects.create()` em testes — use factories em `apps/*/tests/factories.py`. Cobertura de sucesso e falha para `services.py`, e isolamento de tenant para `selectors/`.
* **Frontend:** Proibido mockar chamadas ou hooks Orval por arquivo. Use `test-setup.ts` via `registerMockHook`. Importe utilitários de teste exclusivamente de `@/test-utils`.

---

## 3. Conhecimento & Exemplos Vivos do Repositório

O agente deve se guiar primariamente pelos **exemplos vivos de código** existentes no projeto, pois código testado e validado no CI é a representação mais fiel e atualizada dos padrões arquiteturais:

* **Exemplo de Bounded Context & Serviços Complexos:** [`backend/apps/contracts/`](backend/apps/contracts/) e [`backend/apps/finances/`](backend/apps/finances/).
* **Exemplo de Interfaces Inter-Módulos (ADR-031):** [`backend/apps/contracts/interfaces.py`](backend/apps/contracts/interfaces.py) e [`backend/apps/scheduler/interfaces.py`](backend/apps/scheduler/interfaces.py).
* **Exemplo de Validação AST e Guard-Rails:** [`backend/apps/core/tests/test_commenting_standards.py`](backend/apps/core/tests/test_commenting_standards.py).
* **Exemplo de Smart/Dumb Component no Frontend:** [`frontend/src/features/contracts/`](frontend/src/features/contracts/).

Consulte as skills especializadas quando demandado pelo fluxo em `.agents/skills/`:
* [`.agents/skills/wedding-pr-auditor`](.agents/skills/wedding-pr-auditor/SKILL.md): Auditoria rigorosa pré-merge baseada em evidências ("Evidence over Narrative").
* [`.agents/skills/wedding-business-rules`](.agents/skills/wedding-business-rules/SKILL.md): Catálogo de regras de negócio atômicas (Finanças, Logística, Scheduler, Casamentos).
* [`.agents/skills/wedding-documentation`](.agents/skills/wedding-documentation/SKILL.md): Padrões Diátaxis, MkDocs-First e validação de links.
* [`.agents/skills/tailwind-v4-shadcn`](.agents/skills/tailwind-v4-shadcn/SKILL.md): Configurações e boas práticas de Tailwind CSS v4 com shadcn/ui.
* [`.agents/skills/shadcn`](.agents/skills/shadcn/SKILL.md): Composição e uso de primitivas shadcn/ui.
* [`.agents/skills/react-hook-form`](.agents/skills/react-hook-form/SKILL.md): Otimizações de formulários controlados.
* [`.agents/skills/vitest`](.agents/skills/vitest/SKILL.md): Execução rápida de testes unitários no frontend.

---

## 4. Definição de Pronto (Definition of Done - DoD)

Antes de considerar qualquer tarefa concluída ou abrir PR, os seguintes critérios devem ser estritamente cumpridos:

- [ ] **Active Record Rico:** Invariantes de modelo encapsuladas em `clean()` e validação em 3 níveis (Pydantic $\to$ Model $\to$ Service) respeitada.
- [ ] **Bounded Contexts Isolados:** Zero imports de `models`, `services` ou `managers` de outros módulos; comunicação síncrona exclusiva via `apps.<contexto>.interfaces`.
- [ ] **Multi-Tenancy:** Todo service e selector filtra via `company` e `for_tenant()`.
- [ ] **Contratos de API:** Novos endpoints possuem `operation_id` explícito e os contratos foram sincronizados via `just sync-api`.
- [ ] **Offending Values:** Exceções de negócio e validações interpolam o valor recebido e o formato/valores esperados.
- [ ] **Controle de Fluxo Raso:** Limite de 2 níveis de aninhamento respeitado (guard clauses / early returns aplicados).
- [ ] **Lean Provenance Docstrings:** Docstrings públicas apontam para as regras em `docs/` e ADRs, sem duplicação de tipos.
- [ ] **Zero IA em Comentários:** Nenhum comentário ou docstring contém menções a ferramentas ou assistentes de IA.
- [ ] **Testes com Factories & Fakes:** Proibido `.objects.create()` em testes backend (usar `factories.py`) e proibido mock avulso no frontend (usar `registerMockHook`).
- [ ] **Documentação Diátaxis:** Regras novas ou alteradas documentadas em `docs/architecture/business-rules/` e hubs de domínio atualizados.
- [ ] **Portões de Qualidade Verificados:** Comandos `just check-backend`, `just check-frontend`, `just check-docs` (ou `just check-ci`) executados com código de retorno 0.
