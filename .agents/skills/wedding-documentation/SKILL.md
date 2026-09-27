---
name: wedding-documentation
description: "Documentation standards and workflow for Wedding Management System — MkDocs-First architecture, Rich Domain Hubs, Single Source of Truth (SSOT), atomic business rules, and link checking with just check-docs. Load when creating, editing, or reviewing documentation files under docs/."
---

# Wedding Documentation Playbook

Operational checklist for authoring, refactoring, and reviewing documentation files under `docs/`.

## Documentation Checklist

- [ ] **MkDocs-First Navigation**: The file `mkdocs.yml` is the Single Source of Truth (SSOT) for the documentation tree. Register new pages directly in `mkdocs.yml`. FORBIDDEN to create burocratic intermediate `index.md` files that merely list links.
- [ ] **Rich Domain Hubs (`docs/architecture/domains/`)**: Domain hubs must provide a complete overview of the bounded context, structuring:
  1. Visão de Negócio & Funcionalidades (personas, fluxos operacionais, regras fundamentais).
  2. Modelo de Dados & Diagrama ERD (entidades, chaves, relações e tabela de invariantes de persistência).
  3. Matriz Consolidada de Regras de Negócio (tabela canônica com códigos `BR-XXX`, escopo e fórmulas).
  4. Arquitetura Fullstack (Active Record models ricos, serviços `@transaction.atomic`, selectors CQRS, schemas Pydantic e frontend Smart/Dumb).
  5. Integrações & Interfaces Públicas (`apps.<contexto>.interfaces` - ADR-031).
  6. Aprofundamento (links para notas atômicas de regras complexas e ADRs).
- [ ] **Atomic Business Rules (`docs/architecture/business-rules/`)**: Keep deep mathematical formulas, algorithmic state transitions, or complex domain invariantes in dedicated notes referenced by the Domain Hub.
- [ ] **Cross-Linking Over Duplication**: Never duplicate explanations or code across multiple docs. Use direct Markdown links to the authoritative document (Single Source of Truth - SSOT).
- [ ] **Standard Navigation Header**: Every documentation file under `docs/` MUST begin with a standard PT-BR metadata navigation header:
  ```markdown
  # [Título Claro do Documento]

  > **Categoria:** [Nome da Seção / Subpasta]
  > **Relacionados:** [Link para Nota Relacionada](../caminho/outro-doc.md)
  ```
- [ ] **Language & Tone (PT-BR)**: All documentation under `docs/` MUST be written in Brazilian Portuguese (PT-BR) with proper accents, clear technical terminology, and professional tone.
- [ ] **No AI Mentions**: PROHIBITED to reference AI tools, assistants, or generators (e.g. "Bolt", "Jules", "Copilot", "Claude") in documentation or code comments.
- [ ] **Link Verification**: Always run `just check-docs` (or `uv run --project backend python scripts/validate_docs_links.py`) before committing or submitting Pull Requests to confirm zero broken links.
- [ ] **Reference Documentation**:
  - Technical Specification & Rules: [Documentation Standards](../../../docs/reference/architecture-standards/documentation-standards.md)
  - Practical How-To Guide: [Write and Update Docs Guide](../../../docs/guides/documentation/write-and-update-docs.md)
