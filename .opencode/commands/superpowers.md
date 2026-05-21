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
