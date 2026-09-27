# Especificação Técnica: Workflows de IA (`ai-code-review.yml` & `opencode-assistant.yml`)

> **Módulo:** CI/CD | [ci-pr-validation-spec](ci-pr-validation-spec.md) | [ci-cd-pipeline-flow](../../architecture/concepts/ci-cd-pipeline-flow.md)
> **Workflows:** `.github/workflows/ai-code-review.yml` | `.github/workflows/opencode-assistant.yml`

---

## 1. Visão Geral

Os workflows de IA realizam auditorias automáticas de código e prestam assistência interativa aos desenvolvedores diretamente nos Pull Requests do GitHub.

---

## 2. Workflows Implementados

### 2.1 `ai-code-review.yml` (Revisão Automática por SHA)

- **Gatilho**: Disparado automaticamente na abertura, reabertura ou envio de novos commits (`synchronize`) em Pull Requests direcionados para `develop`.
- **Isolamento de Estado**: Analisa estritamente o diff do SHA atual do commit contra `origin/develop`. Não utiliza labels do GitHub como armazenamento de estado.
- **Auditoria de Qualidade**: Avalia o diff procurando violações de multi-tenancy, queries N+1, falhas de acessibilidade, desvios do Design System e quebras do padrão da camada de serviços (`services.py`).
- **Feedback**: Publica o relatório da revisão como comentário estruturado e sugestões inline (_1-click apply_) no Pull Request.

### 2.2 `opencode-assistant.yml` (Assistente Interativo)

- **Gatilho**: Disparado sob demanda quando um desenvolvedor comenta `/opencode` em um Pull Request ou issue.
- **Capacidade**: Executa diagnósticos de falhas de teste, gera sugestões de refatoração e auxilia na resolução de dúvidas de arquitetura.

---

## 3. Fluxo de Execução da Pipeline (`ai-code-review.yml`)

O diagrama abaixo ilustra o ciclo de vida da Action no GitHub Actions desde o disparo do evento até a execução do job:

```mermaid
flowchart TD
    A["Evento: PR opened / synchronize / reopened"] --> B{"Branch destino é develop?"}
    B -- Não --> C["Ignorar Workflow"]
    B -- Sim --> D{"Alterou apenas *.lock, .gitignore ou .vscode?"}
    D -- Sim --> E["Ignorar Workflow (paths-ignore)"]
    D -- Não --> F{"É Draft PR ou Bot/Dependabot?"}
    F -- Sim --> G["Job Skipped (draft ou dependabot)"]
    F -- Não --> H["Cancelar execuções anteriores no mesmo PR (concurrency)"]
    H --> I["Step 1: Checkout Code (fetch-depth: 0)"]
    I --> J["Step 2: Prepare PR Context, Diff Stat & Diff Content"]
    J --> K["Step 3: Run OpenCode Review (Agente reviewer: steps=10, DeepSeek v4 Pro)"]
    K --> L["Publicação do Comentário / Sugestões Inline no GitHub"]
```

---

## 4. Fluxo de Decisão Interna da IA (System Prompt)

O diagrama abaixo detalha o caminho lógico percorrido pela IA (DeepSeek v4 Pro) ao processar o prompt e avaliar o código do Pull Request:

```mermaid
flowchart TD
    A["Recebe Contexto do PR (Título, Diff Stat, Diff Unificado)"] --> B{"Tipo de Evento: Novo PR ou synchronize?"}
    B -- "synchronize (Novo Commit)" --> C1["1. Checa resolução/justificativas dos itens anteriores"]
    C1 --> C2["2. Exige revisão completa das NOVAS implementações (OBRIGATÓRIO)"]
    B -- "opened / reopened" --> D["Inicia análise do diff completo contra origin/develop"]
    C2 --> D
    D --> E["Inspecionar arquivos alterados no Diff Stat e Diff Unificado"]

    E --> F1{"Altera Backend (backend/)?"}
    F1 -- Sim --> G1["Valida Service Layer, multi-tenancy, operation_id e factories"]

    E --> F2{"Altera Frontend (frontend/, landing/)?"}
    F2 -- Sim --> G2["Valida DESIGN.md, Orval hooks, sem fetch/axios, sem edições em ui/"]

    E --> F3{"Altera Regras de Negócio?"}
    F3 -- Sim --> G3["Valida notas atômicas em docs/architecture/business-rules/"]

    E --> F4{"Altera Documentação (docs/)?"}
    F4 -- Sim --> G4["Valida Diátaxis, Nota Atômica e cross-linking sem duplicação"]

    G1 & G2 & G3 & G4 --> H{"Introduz novos modelos, endpoints ou regras?"}
    H -- Sim --> I{"Documentação em docs/ foi atualizada (Doc Drift)?"}
    I -- Não --> J["Aponta pendência de atualização de documentação"]
    I -- Sim --> K["Filtro de Ruído: Ignora lint/formatação e arquivos .lock"]
    H -- Não --> K
    J --> K

    K --> L{"Houve desvios nas alterações novas ou anteriores?"}
    L -- Não --> M["Emite aprovação: Code Review Aprovado"]
    L -- Sim --> N["Emite sugestões inline (```suggestion) e Tabela Síntese no rodapé"]
```

---

## 5. Diretrizes de Qualidade, Eficiência & Roteamento Dinâmico

1. **Filtro de Bots & Dependabot**: Execuções originadas por bots de atualização de dependências (`dependabot[bot]`) são ignoradas no nível do job, evitando desperdício de saldo em revisões de bumps de pacotes.
2. **Diff Unificado Pré-Injetado**: O step preparatório extrai uma amostra limpa de até 400 linhas do diff (excluindo lockfiles, `openapi.json` e arquivos gerados/minificados), eliminando chamadas redundantes de ferramentas de terminal para descobrir as alterações.
3. **Agente Especializado (`reviewer`) com Step Limiting**: Configurado em `opencode.json` com `mode: primary`, `steps: 10` e permissões de somente leitura (`edit: deny`, `write: deny`), prevenindo loops desnecessários de exploração.
4. **Prefix Caching Optimization**: As regras fixas (`AGENTS.md`, `DESIGN.md`, `SKILL.md`) são mantidas no topo do prompt para aproveitar o _prefix caching_ do DeepSeek (reduzindo custos de tokens de entrada repetidos).
5. **Dupla Checagem em Re-Revisões (`synchronize`)**: A IA é instruída a validar a resolução dos apontamentos anteriores E obrigatoriamente realizar a revisão estática completa de todo o código novo adicionado no commit, evitando aprovação prematura por ancoragem.
6. **Roteamento por Escopo**: A IA consulta apenas as skills e especificações relevantes aos arquivos alterados listados no `Diff Stat`.
7. **Análise Estática Exclusiva**: A IA não executa comandos de shell ou testes durante a revisão, delegando validações dinâmicas às demais pipelines de CI.
8. **Validação de Doc Drift**: Alterações que modifiquem schemas, endpoints ou regras de negócio exigem a atualização ou criação correspondente da nota atômica sob `docs/`.
