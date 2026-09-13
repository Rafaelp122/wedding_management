---
name: wedding-documentation
description: "Documentation standards and workflow for Wedding Management System — Diátaxis framework, Atomic Notes methodology, Single Source of Truth (SSOT), MOC indexes, cross-linking without duplication, and link checking with just check-docs. Load when creating, editing, or reviewing documentation files under docs/."
---

# Wedding Documentation Playbook

Operational checklist for authoring, refactoring, and reviewing documentation files under `docs/`.

## Documentation Checklist

- [ ] **Diátaxis Quadrant Placement**: Classify new documentation strictly into one of the 4 Diátaxis quadrants:
  - `docs/onboarding/`: Onboarding and end-to-end learning guides.
  - `docs/guides/`: Task-oriented practical recipes for developers.
  - `docs/reference/`: Technical specifications, schemas, contracts, and standards.
  - `docs/architecture/`: High-level architecture, design reasoning, and business rules.
- [ ] **Atomic Notes (Single Topic)**: Each Markdown file MUST cover exactly ONE single concept, model, entity, or workflow. If a file begins covering multiple disparate topics, split it into separate atomic notes.
- [ ] **Cross-Linking Over Duplication**: Never duplicate explanations or code across multiple docs. Use direct Markdown links to the authoritative atomic note (Single Source of Truth - SSOT).
- [ ] **MOC (Map of Content) Registration**: Always register new atomic notes in the corresponding folder's `index.md` (MOC) and in [docs/index.md](../../../docs/index.md). Never leave orphan documentation files.
- [ ] **Standard Navigation Header**: Every documentation file under `docs/` MUST begin with a standard PT-BR metadata navigation header:
  ```markdown
  # [Título Claro do Documento]

  > **Categoria:** [Nome do Quadrante / Subpasta]
  > **Relacionados:** [Link para Nota Relacionada](../caminho/outro-doc.md)
  ```
- [ ] **Language & Tone (PT-BR)**: All documentation under `docs/` MUST be written in Brazilian Portuguese (PT-BR) with proper accents, clear technical terminology, and professional tone.
- [ ] **No AI Mentions**: PROHIBITED to reference AI tools, assistants, or generators (e.g. "Bolt", "Jules", "Copilot", "Claude") in documentation or code comments.
- [ ] **Link Verification**: Always run `just check-docs` before committing or submitting Pull Requests to confirm zero broken links.
- [ ] **Reference Documentation**:
  - Technical Specification & Rules: [Documentation Standards](../../../docs/reference/architecture-standards/documentation-standards.md)
  - Practical How-To Guide: [Write and Update Docs Guide](../../../docs/guides/documentation/write-and-update-docs.md)
