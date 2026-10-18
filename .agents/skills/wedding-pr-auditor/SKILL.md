---
name: wedding-pr-auditor
description: "Auditoria rigorosa pré-merge baseada em evidências (Evidence over Narrative) para o Wedding Management System. Executa portões de qualidade, inspeciona diff contra desvios arquiteturais, multi-tenancy, Clean Code para IA e emite parecer binário formal."
---

# Wedding PR Auditor: Verificação Baseada em Evidências

Este playbook estabelece o procedimento hostil de auditoria pré-merge para o **Wedding Management System**.

## 1. Princípio Fundamental: "Evidence over Narrative"

Nenhuma alegação verbal do desenvolvedor ou agente é aceita como verdade sem a saída de terminal comprovando código de retorno `0`. O auditor inspeciona fatos e dados no diff e na execução dos comandos.

---

## 2. Portões de Qualidade Obrigatórios

Execute os comandos abaixo a partir da raiz do projeto e registre os resultados:

```bash
# 1. Checagem estrita de fronteiras modulares e arquitetura (ADR-031)
just arch

# 2. Suíte de testes do backend com tipagem e linting
just check-backend

# 3. Suíte de testes e tipos do frontend
just check-frontend

# 4. Auditoria de integridade documental e links
just check-docs
```

> **Regra de Bloqueio:** Se qualquer comando retornar código diferente de zero ou emitir warnings não justificados, a auditoria é interrompida imediatamente com status `[REPROVADO COM PENDÊNCIAS]`.

---

## 3. Checklist Hostil de Inspeção do `git diff`

O auditor deve analisar o `git diff origin/develop...HEAD` (ou branch alvo) procurando ativamente pelos seguintes desvios:

### A. Fronteiras de Bounded Contexts (ADR-031)
- [ ] O código importa `models`, `services` ou `managers` de outro app diretamente? (**PROIBIDO**).
- [ ] Toda a comunicação síncrona transacional entre módulos passa exclusivamente por `apps.<contexto>.interfaces`?
- [ ] Efeitos secundários desacoplados utilizam `django.tasks` enfileiradas pós-commit via `transaction.on_commit`?
- [ ] Consultas analíticas multi-domínio residem exclusivamente em `apps/reporting`?

### B. Multi-Tenancy & Segurança (ADR-009, ADR-016)
- [ ] Todo service e selector aceita o parâmetro `company: Company` e filtra com `for_tenant(company)`?
- [ ] Lookups individuais de entidades utilizam `validate_tenant_ownership` ou `get_object_or_404_for_tenant`?
- [ ] Há uso de `.objects.all()` ou `.objects.filter()` sem escopo de tenant em modelos herdados de `TenantModel`? (**PROIBIDO**).

### C. Rich Active Record & YAGNI (ADR-006, ADR-011, ADR-030)
- [ ] Invariantes de modelo e transições de estado residem no método `clean()` da entidade?
- [ ] Há lógica procedural em services alterando campos de status diretamente sem chamar métodos de ciclo de vida do model? (**PROIBIDO**).
- [ ] Há métodos ou propriedades (`@property`) criados de forma especulativa sem consumidor de produção imediato? (**PROIBIDO**).

### D. Clean Code para Agentes de IA (Akita, 2026)
- [ ] **Nomes Greppáveis:** Símbolos públicos (classes, métodos de serviço, interfaces, exceções) são distintivos e retornam `< 5 matches` no `rg`? Proibido `data`, `handler`, `Manager`, `process()`.
- [ ] **Offending Values:** Exceções de domínio e validações interpolam o valor causador e o conjunto esperado (ex.: `f"Status '{status}' inválido; esperados: {sorted(ALLOWED)}")`?
- [ ] **Aninhamento Raso:** O código respeita o teto de **máximo 2 níveis** de controle de fluxo (`if/for/try/with`), aplicando guard clauses e early returns?
- [ ] **Funções Curtas:** Funções possuem entre 4 e 20 linhas (máximo 30 em orquestrações complexas)?
- [ ] **Lean Provenance Docstrings:** Métodos públicos contêm resumo conciso de negócio, referência à regra canônica (`BR-XXX`) e ADR em `docs/`, `Efeitos Colaterais:` e `Raises:`? Zero tipos redundantes em docstring.
- [ ] **Zero IA em Comentários:** Há menções a ferramentas de IA ("Bolt", "Jules", "Copilot", "gerado por IA")? (**PROIBIDO**).

### E. Integridade de Testes & Frontend
- [ ] Há chamadas diretas a `.objects.create()` nos testes backend? (**PROIBIDO** — use factories em `apps/*/tests/factories.py`).
- [ ] No frontend, há mocks locais ad-hoc de hooks de dados? (**PROIBIDO** — use `test-setup.ts` via `registerMockHook`).
- [ ] No frontend, há chamadas diretas a `fetch` ou `axios`? (**PROIBIDO** — use hooks do Orval via `just sync-api`).
- [ ] Componentes seguem o padrão Smart/Dumb (ADR-024)?

---

## 4. Template Canônico de Saída

O auditor deve emitir obrigatoriamente um relatório no seguinte formato:

```markdown
# Relatório de Auditoria Pré-Merge

- **Branch:** <nome-da-branch>
- **Target:** develop
- **Data/Hora:** <YYYY-MM-DD HH:MM:SS>

## 1. Evidências dos Portões de Qualidade
- [x] `just arch`: PASS (Tach zero violações)
- [x] `just check-backend`: PASS (Ruff, Mypy, Pytest 100%)
- [x] `just check-frontend`: PASS (Lint, Types, Vitest 100%)
- [x] `just check-docs`: PASS (Links e snippets 100%)

## 2. Auditoria do Diff
- **Arquivos Inspecionados:** <N> arquivos
- **Bounded Contexts:** Conforme / Violado
- **Multi-Tenancy:** Conforme / Violado
- **Clean Code para IA:** Conforme / Violado
- **Testes (Factories):** Conforme / Violado

## 3. Parecer Final

[APROVADO PARA MERGE]
<!-- OU -->
[REPROVADO COM PENDÊNCIAS]

### Pendências Bloqueantes (se houver):
1. `<arquivo>:<linha>` — Violação do padrão X: explicação do desvio e comando de correção.
```
