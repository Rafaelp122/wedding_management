# Especificação Técnica: Padrões de Documentação (MkDocs-First & Hubs de Domínio)

> **Módulo:** Padrões de Arquitetura & Engenharia | [docs-readme](../../index.md)
> **Camada:** Documentação do Projeto (`docs/`)

---

## 1. Visão Geral

Toda a documentação técnica do **Wedding Management System** sob o diretório `docs/` segue o paradigma **MkDocs-First**, estruturado em **Hubs de Domínio Ricos** (`docs/architecture/domains/`), **Regras de Negócio SSOT** (`docs/architecture/business-rules/`) e **Guias Práticos Operacionais**.

A árvore hierárquica do [`mkdocs.yml`](../../../mkdocs.yml) atua como a **Única Fonte da Verdade (SSOT)** para toda a navegação, eliminando a sobrecarga de MOCs intermediários.

---

## 2. Princípios Fundamentais de Autoria

### 2.1 Hubs de Domínio Ricos (Single Source of Truth de Domínio)
- Cada Bounded Context da aplicação possui um Hub canônico em `docs/architecture/domains/` que consolida a visão de produto/negócio, diagrama de dados ERD com invariantes, matriz de regras de negócio, arquitetura técnica fullstack e interfaces públicas (ADR-031).

### 2.2 Princípio de Cross-Linking (Sem Duplicação de Conteúdo)
- **Single Source of Truth (SSOT)**: A explicação técnica de um assunto deve residir em exatamente um único arquivo canônico.
- **Link ao Invés de Repetição**: Se um documento precisar mencionar outro tópico, **É PROIBIDO duplicar o texto**. Em vez disso, insira um link Markdown direto para o arquivo especializado.

### 2.3 Navegação MkDocs-First (Sem MOCs Burocráticos)
- Toda e qualquer nova página deve ser registrada diretamente no `mkdocs.yml`.
- É **PROIBIDO** criar arquivos `index.md` intermediários em subpastas com o único propósito de listar links que já aparecem na barra lateral do MkDocs.

### 2.4 Desacoplamento de Código e Proibição de Snippets Numéricos
- **Proibição Estrita de Faixas Numéricas (`:start:end`):** É terminantemente proibido o uso de transclusões baseadas em números de linha (ex.: `--8<-- arquivo.py:10:25`). Alterações cotidianas como novas importações ou formatação deslocam silenciosamente essas faixas, provocando *code-drift* e exibindo trechos quebrados na documentação.
- **Padrão Canônico ADR-030 (Links Semânticos + Blocos Estáveis):** Documente o comportamento do sistema apresentando blocos conceituais estáveis acompanhados de links diretos para as classes, métodos ou testes (ex.: `[Supplier.clean()](../../backend/apps/logistics/models/supplier.py)`).
- **Tags Semânticas Delimitadas (Exceção Controlada):** Caso seja indispensável transcluir um trecho literal de código, utilize exclusivamente marcadores semânticos nomeados no arquivo fonte (`# --8<-- [start:tag_name]` e `# --8<-- [end:tag_name]`), devidamente validados pelo CI (`scripts/validate_docs_snippets.py`).
- **Rastreabilidade Bidirecional (*Code $\leftrightarrow$ Docs*):** Documentos de regras de negócio (`BR-XXX`) e decisões (`ADR-XXX`) devem apontar para seus respectivos símbolos em código, enquanto as docstrings do Python referenciam a documentação canônica (conforme [ADR-021](../../architecture/adr/021-padrao-comentarios-docstrings.md)).

---

## 3. Quadrantes da Metodologia Diátaxis

Toda nova documentação deve ser classificada em um dos 4 quadrantes do Diátaxis sob a pasta correspondente:

| Quadrante | Diretório | Foco do Leitor | Conteúdo Permitido |
|:---|:---|:---|:---|
| **1. Tutorials** | `docs/onboarding/` | Aprendizado & Onboarding | Guias passo a passo guiados para iniciantes no projeto (ex: subir ambiente local). |
| **2. How-To Guides** | `docs/guides/` | Resolução de Problemas | Receitas práticas e orientadas a tarefas do dia a dia (ex: como gerar cliente Orval). |
| **3. Reference** | `docs/reference/` | Especificação Técnica | Descrições técnicas puras, schemas de banco, contratos de API e padrões. |
| **4. Explanation** | `docs/architecture/` | Compreensão e Arquitetura | Contexto profundo de design, regras de negócio atômicas e ADRs. |

---

## 4. Estilo, Idioma e Convenções

1. **Idioma Oficial**: Toda a documentação sob `docs/` deve ser escrita em **Português do Brasil (PT-BR)** técnico, claro, acentuado e gramaticalmente correto.
2. **Sem Referências a Geradores/Ferramentas de IA**: É estritamente **PROIBIDO** mencionar assistentes de IA, geradores automáticos ou ferramentas de chat nos textos da documentação.
3. **Formatação e Alertas GitHub**:
   - Utilize alertas nativos do GitHub (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!WARNING]`) com parcimônia para destacar avisos críticos.
   - Utilize diagramas Mermaid (````mermaid`) para ilustrar fluxos de arquitetura ou estados complexos.

---

## 5. Validação Automatizada de Links (`just check-docs`)

Para garantir que nenhum link para notas atômicas seja quebrado durante refatorações:

```bash
just check-docs
```

A pipeline de CI ([docs-ci.yml](../../../.github/workflows/docs-ci.yml)) executa `just check-docs` em todo Pull Request e rejeita alterações com links de documentação quebrados ou inválidos.
