# Integrate Superpowers Skills into Wedding Management

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate superpowers workflow skills into the project via a `/superpowers` command, AGENTS.md references, and enriched sub-agent instructions.

**Architecture:** Single pipeline command (`/superpowers`) triggers the full brainstorming→plan→execute→finish flow. Sub-agents gain domain-specific skill references. AGENTS.md gets a lightweight pointer section. No forced pipeline — skills remain opt-in for daily use.

**Tech Stack:** OpenCode custom commands (markdown), agent markdown files.

---

### Task 1: Create `/superpowers` Command

**Files:**
- Create: `.opencode/commands/superpowers.md`

- [ ] **Step 1: Write the command file**

`.opencode/commands/superpowers.md`:
```markdown
---
description: Pipeline completo superpowers — brainstorming, spec, plano, implementação com TDD, revisão, finalização
agent: build
---

Você vai executar o fluxo completo de desenvolvimento superpowers para a seguinte tarefa:

"$ARGUMENTS"

Siga estas fases em ordem, uma por vez, sem pular etapas:

### Fase 1: Brainstorming
Carregue a skill `brainstorming`. Explore o que foi pedido, faça perguntas para refinar, proponha abordagens, apresente o design para aprovação, e escreva a spec.

### Fase 2: Plano de Implementação
Carregue a skill `writing-plans`. Transforme a spec aprovada em um plano detalhado com tarefas bite-size, salve em `docs/superpowers/plans/`.

### Fase 3: Execução
Carregue a skill `using-git-worktrees` para isolar o workspace. Depois carregue `subagent-driven-development` para implementar tarefa por tarefa com TDD (`test-driven-development`) e revisão (`requesting-code-review`) entre cada uma.

### Fase 4: Finalização
Carregue `verification-before-completion` para rodar verificações. Depois carregue `finishing-a-development-branch` para apresentar as opções de merge/PR.

Regras:
- NUNCA pule fases sem confirmar com o usuário
- Se encontrar bugs, carregue `systematic-debugging` ANTES de corrigir
- Sempre use `test-driven-development` para qualquer código novo
```

- [ ] **Step 2: Commit**

```bash
git add .opencode/commands/superpowers.md
git commit -m "feat(superpowers): add /superpowers pipeline command"
```

---

### Task 2: Update AGENTS.md

**Files:**
- Modify: `AGENTS.md` (append after line 55)

- [ ] **Step 1: Append Superpowers Workflow section**

Add after the last line of `AGENTS.md`:

```markdown
## 🦾 Superpowers Workflow

Skills de processo disponíveis em `.agents/skills/`. O agente DEVE carregá-las via `Skill` tool quando relevante.

### Fluxo completo (para features, refactors, bugs complexos)
Use o comando `/superpowers "descrição da tarefa"` para ativar o pipeline:
brainstorming → spec → plano → implementação com TDD → revisão → finalização.

### Skills individuais (uso diário)
| Situação | Skill |
|----------|-------|
| Criar feature, componente, ou mudar comportamento | `brainstorming` |
| Implementar feature ou corrigir bug | `test-driven-development` |
| Encontrar bug, teste quebrado, comportamento inesperado | `systematic-debugging` |
| Antes de declarar "pronto", commitar, ou criar PR | `verification-before-completion` |
| Revisar PR ou diff | `pr-reviewer` |
| Receber feedback de code review | `receiving-code-review` |
| Finalizar branch (merge, PR, descarte) | `finishing-a-development-branch` |
```

- [ ] **Step 2: Commit**

```bash
git add AGENTS.md
git commit -m "docs(superpowers): add superpowers workflow section to AGENTS.md"
```

---

### Task 3: Enrich backend and frontend agents

**Files:**
- Modify: `.opencode/agents/backend.md` (append after line 75)
- Modify: `.opencode/agents/frontend.md` (append after line 76)

- [ ] **Step 1: Append to backend.md**

```markdown
### 🦾 Superpowers Skills

Para tasks complexas, sugira ao usuário o comando `/superpowers`. Para uso diário:

- **Antes de escrever código novo:** carregue a skill `test-driven-development` — escreva o teste, veja falhar, implemente o mínimo
- **Ao encontrar bugs ou testes quebrados:** carregue `systematic-debugging` — investigue causa raiz antes de corrigir
- **Antes de declarar tarefa concluída:** carregue `verification-before-completion` — rode verificações e mostre evidência
```

- [ ] **Step 2: Append same block to frontend.md**

Same content appended to end of `.opencode/agents/frontend.md`.

- [ ] **Step 3: Commit**

```bash
git add .opencode/agents/backend.md .opencode/agents/frontend.md
git commit -m "docs(superpowers): enrich backend and frontend sub-agents with superpowers skills"
```

---

### Task 4: Enrich test-writer agent

**Files:**
- Modify: `.opencode/agents/test-writer.md` (append after line 78)

- [ ] **Step 1: Append**

```markdown
### 🦾 Superpowers Skills

- **Sempre use `test-driven-development`:** escreva o teste primeiro, veja falhar, confirme que testa o comportamento correto
- **Antes de declarar concluído:** carregue `verification-before-completion` — execute os testes e mostre o output
```

- [ ] **Step 2: Commit**

```bash
git add .opencode/agents/test-writer.md
git commit -m "docs(superpowers): enrich test-writer sub-agent with superpowers skills"
```

---

### Task 5: Enrich remaining agents (pr-reviewer, general, design)

**Files:**
- Modify: `.opencode/agents/pr-reviewer.md` (append after line 47)
- Modify: `.opencode/agents/general.md` (append after line 45)
- Modify: `.opencode/agents/design.md` (append after line 51)

- [ ] **Step 1: Append to pr-reviewer.md**

```markdown
### 🦾 Superpowers Skills

- **Para revisar código:** carregue `requesting-code-review` para o template de dispatch do revisor
- **Se o autor responder ao seu feedback:** carregue `receiving-code-review` para processar contra-argumentos tecnicamente
```

- [ ] **Step 2: Append to general.md**

```markdown
### 🦾 Superpowers Skills

- **Para features complexas:** sugira ao usuário o comando `/superpowers "descrição"` que ativa o pipeline completo
- **Para debugging sistemático:** carregue `systematic-debugging` antes de propor fixes
- **Antes de declarar concluído:** carregue `verification-before-completion`
```

- [ ] **Step 3: Append to design.md**

```markdown
### 🦾 Superpowers Skills

- **Antes de criar interfaces:** carregue `brainstorming` para explorar direção estética, validar com usuário, e escrever spec antes de codar
```

- [ ] **Step 4: Commit**

```bash
git add .opencode/agents/pr-reviewer.md .opencode/agents/general.md .opencode/agents/design.md
git commit -m "docs(superpowers): enrich pr-reviewer, general, and design sub-agents with superpowers skills"
```

---

### Task 6: Verify

- [ ] **Step 1: Verify all files exist and have correct content**

```bash
ls -la .opencode/commands/superpowers.md
wc -l AGENTS.md .opencode/agents/*.md
```

- [ ] **Step 2: Git status check**

```bash
git status
git log --oneline -5
```
