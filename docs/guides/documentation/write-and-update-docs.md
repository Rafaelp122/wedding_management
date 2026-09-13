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

---

## Passo 4: Atualizar os Índices (MOC e `docs/index.md`)

Para garantir que a nota não fique "órfã" e inacessível:

1. Adicione o link para o novo arquivo no `index.md` (MOC) da subpasta onde ele foi criado.
2. Registre a nova nota na seção correspondente do [docs/index.md](../../index.md).

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
