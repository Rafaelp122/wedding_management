# Especificação Técnica: Padrões de Documentação (Diátaxis & Notas Atômicas)

> **Módulo:** [architecture-standards](index.md) | [docs-readme](../../index.md)
> **Camada:** Documentação do Projeto (`docs/`)

---

## 1. Visão Geral

Toda a documentação técnica do **Wedding Management System** sob o diretório `docs/` segue estritamente a metodologia **Diátaxis** combinada com o princípio de **Notas Atômicas** e **Single Source of Truth (SSOT)**.

Esta diretriz estabelece as regras de autoria, estruturação, vinculação e manutenção dos arquivos de documentação do repositório.

---

## 2. Princípios Fundamentais de Autoria

### 2.1 Princípio da Nota Atômica (Assunto Único)
- **Um Único Tópico por Arquivo**: Cada arquivo Markdown (`.md`) deve ser dedicado a **apenas um único conceito, entidade, modelo ou procedimento**.
- **Sem Monólitos**: Se um documento começar a abordar múltiplos assuntos distintos (ex: juntar testes de backend, frontend e infraestrutura em um único arquivo), ele **DEVE** ser dividido em notas atômicas separadas.

### 2.2 Princípio de Cross-Linking (Sem Duplicação de Conteúdo)
- **Single Source of Truth (SSOT)**: A explicação técnica de um assunto deve residir em exatamente um único arquivo de referência.
- **Link ao Invés de Repetição**: Se um documento precisar mencionar outro tópico (ex: a especificação de CI/CD mencionar os gates de testes automatizados), **É PROIBIDO duplicar o texto**. Em vez disso, insira um link Markdown direto para a nota atômica especializada:
  ```markdown
  <!-- ✅ CORRETO: Link para a nota atômica especializada -->
  Para a especificação detalhada dos testes nativos do Terraform, consulte [terraform-testing-spec](../testing/terraform-testing-spec.md).

  <!-- ❌ ERRADO: Redigitar as regras e códigos de teste do Terraform dentro do arquivo de CI/CD -->
  ```

### 2.3 Map of Content (MOC / Arquivos `index.md`)
- Pastas que agrupam múltiplas notas atômicas (ex: `docs/reference/models/`, `docs/reference/testing/`, `docs/architecture/business-rules/`) devem conter um arquivo `index.md` atuando como **MOC (Map of Content)**.
- O MOC fornece uma introdução sucinta e uma lista organizada de links para todas as notas atômicas daquela categoria.

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

## 5. Validação Automatizada de Links (`make check-docs`)

Para garantir que nenhum link para notas atômicas seja quebrado durante refatorações:

```bash
make check-docs
```

A pipeline de CI ([docs-ci.yml](../../../.github/workflows/docs-ci.yml)) executa `make check-docs` em todo Pull Request e rejeita alterações com links de documentação quebrados ou inválidos.
