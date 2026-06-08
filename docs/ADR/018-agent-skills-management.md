# ADR-018: Gestão de Skills para Agentes de IA

## Status
Aceito

## Contexto
O projeto Wedding Management utiliza agentes de IA (via OpenCode) para automatizar tarefas de revisão de PR, geração de descrições, análise estática e testes. As instruções para esses agentes residem em arquivos de skill (`.agents/skills/`), que são versionados no repositório e referenciados no `AGENTS.md`.

Com o crescimento do sistema, surgiu a necessidade de expandir o catálogo de skills para cobrir novos domínios:

- **Dashboards interativos**: Construção de painéis HTML autocontidos com gráficos, filtros e tabelas para relatórios executivos.
- **Padrões de composição React**: Diretrizes para refatorar componentes com proliferação de props booleanas, construir bibliotecas de componentes flexíveis e projetar APIs reutilizáveis.

## Decisão
Adicionamos dois novos skills ao repositório, registrados no arquivo `skills-lock.json`:

1. **`build-dashboard`** (fonte: `anthropics/knowledge-work-plugins`): Habilita a geração de dashboards HTML interativos com KPI cards, gráficos e tabelas. Útil para criar visões executivas e relatórios compartilháveis.

2. **`vercel-composition-patterns`** (fonte: `vercel-labs/agent-skills`): Fornece padrões de composição React que escalam, como compound components, render props e context providers. Alinhado com React 19.

### Critérios de seleção
- Skills de fontes oficiais (Anthropic, Vercel) com manutenção ativa
- Complementam as necessidades atuais do projeto (dashboards e composição de componentes)
- Não conflitam com skills existentes
- Leves: não adicionam dependências de runtime ao projeto

### Registro
Os skills são registrados em `skills-lock.json` com hash de integridade (`computedHash`) para garantir reprodutibilidade. O `AGENTS.md` já referencia ambos na tabela de skills disponíveis.

## Consequências

### Positivas
- Agentes de IA podem gerar dashboards HTML interativos sob demanda
- Refatorações de componentes React seguem padrões de composição testados
- Skills versionados garantem consistência entre ambientes de desenvolvimento

### Negativas
- Aumento marginal no tamanho do repositório (arquivos `.md` de skills)
- Manutenção: updates de skills exigem atualização de hash no `skills-lock.json`
