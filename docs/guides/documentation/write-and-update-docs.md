# Como Criar ou Atualizar Documentação Técnica no Repositório

> **Categoria:** How-To Guide (`guides/documentation`)
> **Relacionados:** [documentation-standards](../../reference/architecture-standards/documentation-standards.md) | [Task Runner Just](../dev-environment/task-runner-just.md)

---

## Visão Geral

Este guia passo a passo orienta desenvolvedores e contribuidores sobre como criar ou atualizar documentação técnica no repositório seguindo a metodologia **Diátaxis** e o princípio de **Notas Atômicas**.

---

## Passo 1: Determinar o Quadrante Correto no Diátaxis

Antes de criar um arquivo, identifique o objetivo do seu texto e escolha a pasta correta:

| Se o objetivo é... | Escolha o Quadrante | Pasta Target |
|:---|:---|:---|
| Ensinar um fluxo completo para um iniciante (onboarding) | **1. Tutorials** | `docs/onboarding/` |
| Fornecer uma receita prática passo a passo para resolver uma tarefa | **2. How-To** | `docs/guides/<categoria>/` |
| Especificar um modelo de banco, contrato de API ou padrão técnico | **3. Reference** | `docs/reference/<categoria>/` |
| Explicar o raciocínio de design, arquitetura ou regra de negócio | **4. Explanation** | `docs/architecture/<categoria>/` |

---

## Passo 2: Verificar a Existência de Nota Atômica

1. Pesquise no diretório `docs/` se já existe uma nota sobre o assunto:
   ```bash
   find docs/ -name "*<assunto>*.md"
   ```
2. **Regra do Assunto Único**:
   - Se a nota atômica já existir, edite-a preservando o foco exclusivo no assunto.
   - Se você estiver adicionando um tópico totalmente novo (ex: um novo modelo de banco ou novo módulo), crie um novo arquivo `.md`.
   - **NUNCA** adicione um tópico heterogêneo dentro de uma doc existente (ex: não coloque regras de testes de frontend dentro de uma doc de infraestrutura).

---

## Passo 3: Escrever a Nota Atômica Usando o Template Padrão

Crie o arquivo Markdown contendo obrigatoriamente o cabeçalho de navegação:

```markdown
# [Título Claro e Descritivo do Assunto]

> **Categoria:** [Nome do Quadrante/Módulo]
> **Relacionados:** [Link para Doc Relacionada](../caminho/outro-doc.md)

---

## 1. Visão Geral

[Explicação direta e focada no único assunto da nota.]

---

## 2. Conteúdo Principal

[Tabelas, código, regras ou especificações.]
```

### Regra Importante de Cross-Linking:
Se o texto precisar mencionar outro conceito (ex: como o CI valida a doc), **NÃO** redigite a explicação. Insira apenas um link para a nota existente:
```markdown
<!-- CORRETO: Link direto para a nota responsável -->
A validação de links da documentação é explicada em [documentation-standards](../../reference/architecture-standards/documentation-standards.md).
```

### Desacoplamento de Código e Rastreabilidade Bidirecional:
- **Evite Snippets Numéricos:** Nunca use transclusões baseadas em linhas (`--8<-- caminho:inicio:fim`). O CI rejeitará snippets com faixas numéricas de linhas.
- **Prefira Links Canônicos (ADR-030):** Explique o comportamento ou regra conceitualmente e forneça links navegáveis para os símbolos em código:
  ```markdown
  - Regra implementada em: [`ContractService.create_contract()`](../../backend/apps/logistics/services/contract_service.py)
  - Validação de integridade: [`Contract.clean()`](../../backend/apps/logistics/models/contract.py)
  ```
- **Rastreabilidade Bidirecional (*Code $\leftrightarrow$ Docs*):** Ao criar regras atômicas de negócio (`BR-XXX`) ou decisões arquiteturais (`ADR-XXX`), registre a referência cruzada na docstring do método no código (`Regra de Negócio: BR-XXX (docs/...)`) para fechar o ciclo de auditoria contínua.

---

## Passo 4: Registrar a Navegação no MkDocs (`mkdocs.yml`)

Para garantir que o documento seja navegável e indexado:

1. **Árvore de Navegação (SSOT):** Adicione a nova página diretamente na seção apropriada do [`mkdocs.yml`](../../../mkdocs.yml). É expressamente proibido criar arquivos `index.md` intermediários apenas para listar links (eliminação de MOCs burocráticos).
2. **Hubs de Domínio & Regras:** Se o novo arquivo for uma regra de negócio (`BR-*`), registre-a na tabela canônica do seu respectivo Hub de Domínio (`docs/architecture/domains/`) e no [Catálogo Geral de Regras](../../architecture/business-rules/index.md).

---

## Passo 5: Validar os Links Locais

Antes de abrir o Pull Request ou realizar o commit, execute a validação de documentação:

```bash
# Via Just (Recomendado):
just check-docs

# Ou Trilha Nativa Direta:
uv run --project backend python scripts/validate_docs_links.py && \
uv run --project backend python scripts/validate_docs_snippets.py && \
npx -y @google/design.md lint DESIGN.md && \
uv run --project backend --group docs mkdocs build --strict
```

Se o comando concluir sem erros, sua documentação está pronta e validada para integração no repositório!
