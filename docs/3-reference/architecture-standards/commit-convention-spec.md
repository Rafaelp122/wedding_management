# Especificação Técnica: Padrão de Commits (Conventional Commits)

> **Módulo:** [architecture-standards](index.md) | [gitops-sprint-workflow](../../1-tutorials/gitops-sprint-workflow.md)
> **Camada:** Controle de Versão & Git Ops

---

## 1. Visão Geral

O **Wedding Management System** adota estritamente a especificação **Conventional Commits (v1.0.0)** para todas as mensagens de commit no repositório.

Esta padronização garante histórico limpo, rastreabilidade automática no Git, geração de changelogs e integração com pipelines de CI/CD.

---

## 2. Formato da Mensagem

Toda mensagem de commit DEVE seguir o seguinte formato:

```text
<tipo>(<escopo opcional>): <descrição sucinta em PT-BR>

[corpo opcional explicando o PORQUÊ da alteração]

[rodapé opcional: refs #issue ou BREAKING CHANGE: ...]
```

---

## 3. Tipos Permitidos (`types`)

| Tipo | Quando Utilizar | Exemplo |
|:---|:---|:---|
| **`feat`** | Adição de nova funcionalidade ou endpoint | `feat(finances): implementa parcelamento de despesas` |
| **`fix`** | Correção de bug ou falha de produção | `fix(auth): corrige vazamento de sessão de usuário` |
| **`docs`** | Adição ou alteração de documentação em `docs/` | `docs(testing): adiciona especificação técnica do Pytest` |
| **`refactor`** | Alteração de código sem mudar comportamento | `refactor(services): simplifica consulta ORM em fornecedores` |
| **`test`** | Adição ou refatoração de testes unitários/E2E | `test(frontend): adiciona testes de integração com MSW` |
| **`chore`** | Tarefas de manutenção, pacotes ou CI | `chore(deps): atualiza dependências do pnpm` |
| **`style`** | Ajustes de formatação que não afetam o código | `style(landing): ajusta espaçamento do componente Hero` |

---

## 4. Diretrizes de Mensagem

1. **Idioma**: Escreva a mensagem em **Português do Brasil (PT-BR)**, em letras minúsculas e no imperativo/presente (ex: `adiciona`, `corrige`, `implementa`).
2. **Escopo Opção**: O escopo indica o módulo alterado (ex: `finances`, `notifications`, `auth`, `terraform`, `docs`).
3. **Sem AI Mentions**: É estritamente **PROIBIDO** mencionar assistentes ou ferramentas de IA nas mensagens de commit.
