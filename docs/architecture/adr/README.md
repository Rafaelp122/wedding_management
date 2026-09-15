# Architecture Decision Records (ADRs)

> **Módulo:** [system-overview](../concepts/system-overview.md) | [docs-portal](../../index.md)
> **Escopo:** Catálogo Oficial de Decisões Arquiteturais e Registros de Trade-offs do Projeto

---

## 1. Visão Geral

Esta pasta reúne todos os **Architecture Decision Records (ADRs)** do Wedding Management System. Cada ADR documenta uma decisão estrutural relevante, seu contexto, alternativas consideradas e as consequências arquiteturais adotadas.

> **Nota de Numeração Imutável:** A numeração das ADRs é mantida estritamente imutável para preservar a rastreabilidade histórica no código-fonte, comentários de classe e mensagens de commit do Git. A identificação `ADR-015` refere-se a uma proposta descontinuada na fase inicial do projeto, mantendo-se a sequência oficial das 29 decisões registradas.

---

## 2. Legenda do Ciclo de Vida das Decisões

| Status | Significado Arquitetural |
| :--- | :--- |
| 🟢 **Vigente** | Decisão ativa que governa o padrão atual de código e arquitetura. |
| 🟡 **Superada** | Decisão histórica substituída por uma abordagem mais madura em ADR posterior. |
| 🟡 **Consolidada** | Decisão cujo escopo foi incorporado integralmente dentro de outra ADR mais abrangente. |
| 🟡 **Emendada** | Decisão vigente que teve cláusulas ou diretrizes pontualmente ajustadas por ADR posterior. |
| ⚪ **Descontinuada** | Proposta preliminar descartada antes de entrar em operação. |

---

## 3. Decisões Arquiteturais Vigentes

### Backend, Domínio & Integridade de Dados
- **[ADR-007: Hybrid Keys](007-hybrid-keys.md)** 🟢 — Chaves híbridas: BigInt sequencial interno e UUID v4 público em endpoints da API.
- **[ADR-010: Tolerância Zero](010-tolerance-zero.md)** 🟢 — Princípio contábil da divisão exata de parcelas sem perda de centavos no arredondamento.
- **[ADR-011: BaseModel full_clean()](011-basemodel-save-full-clean.md)** 🟢 — Execução automática da validação de invariantes no `save()`, pilar do Nível 2 na [ADR-030](030-rich-domain-model-service-layer.md).
- **[ADR-013: Django Ninja API](013-migrate-drf-to-ninja.md)** 🟢 — Substituição do DRF pelo Django Ninja por alta performance e tipagem Pydantic nativa.
- **[ADR-014: Tipagem Estática Estrita (mypy)](014-adocao-tipagem-estatica-mypy.md)** 🟢 — Adoção de checagem estática de tipos no backend Python.
- **[ADR-016: Pragmatic Multi-tenancy](016-pragmatic-multi-tenancy.md)** 🟢 — Multi-tenancy corporativo (`Company` / `TenantModel`), `TenantManager` e validação defensiva.
- **[ADR-017: Async Task Infrastructure](017-async-task-infrastructure.md)** 🟢 — Infraestrutura de tarefas assíncronas e agendadas.
- **[ADR-022: Static Routes Optimization](022-static-routes-for-performance.md)** 🟢 — Priorização de rotas estáticas sobre dinâmicas para evitar colisão e otimizar latência.
- **[ADR-023: Desacoplamento dos Módulos Core e Extração do Módulo Reporting](023-desacoplamento-modulos-scheduler-finances-weddings.md)** 🟢 — Desacoplamento modular e extração do app dedicado de relatórios.
- **[ADR-030: Rich Domain Model e Service Layer como Casos de Uso](030-rich-domain-model-service-layer.md)** 🟢 — Rich Active Record no Django, 3 Níveis Formais de Validação e Service Layer como orquestradora.

### Frontend, UX & Padrões de Qualidade
- **[ADR-012: Orval Contract-Driven API](012-orval-contract-driven-frontend.md)** 🟢 — Geração de hooks React Query e tipos TypeScript a partir do OpenAPI schema do Django Ninja.
- **[ADR-018: Playwright E2E Testing](018-playwright-e2e-testing.md)** 🟢 — Testes de integração end-to-end do frontend com Playwright.
- **[ADR-021: Commenting & Docstring Standards](021-padrao-comentarios-docstrings.md)** 🟢 — Padrão de comentários no código e Google Style docstrings em PT-BR para regras de negócio.
- **[ADR-024: Smart/Dumb Components Pattern](024-padrao-smart-dumb-desacoplamento-componentes-frontend.md)** 🟢 — Separação entre componentes inteligentes (dados/rotas) e apresentacionais desacoplados.
- **[ADR-028: Diátaxis & Anotações Atômicas](028-diataxis-atomic-notes.md)** 🟡 *(Emendada)* — Framework Diátaxis e notas atômicas, com diretriz pragmática de links da [ADR-030](030-rich-domain-model-service-layer.md) (§ 3).

### Infraestrutura, DevOps & Cloud
- **[ADR-001: Cloud Run](001-why-cloud-run.md)** 🟢 — Hospedagem Serverless do Backend Django Ninja no GCP Cloud Run.
- **[ADR-002: Neon PostgreSQL](002-why-neon.md)** 🟢 — Banco de dados PostgreSQL Serverless com suporte a Database Branching.
- **[ADR-003: Cloudflare R2](003-why-r2.md)** 🟢 — Armazenamento de PDFs e anexos com custo zero de transferência (egress).
- **[ADR-004: Presigned URLs](004-presigned-urls.md)** 🟢 — Upload direto e seguro de contratos para o R2 sem sobrecarregar o backend.
- **[ADR-005: Cloud Scheduler & OIDC](005-oidc-scheduler.md)** 🟢 — Automação de tarefas cron via requisições autenticadas por OIDC Service Accounts.
- **[ADR-020: StorageService Abstraction](020-storage-service-abstraction.md)** 🟢 — Camada de abstração e injeção de dependência de serviço de storage.
- **[ADR-025: Terraform & GitOps](025-terraform-iac-architecture.md)** 🟢 — Infraestrutura como código (IaC), ownership e automação GitOps multi-cloud.
- **[ADR-026: Estratégia de Branches & Staging](026-gitops-branching-and-deployment-strategy.md)** 🟢 — Modelo de branches (`main`/`develop`), homologação privada e ciclo por Sprints.
- **[ADR-027: Topologia dos States Terraform](027-terraform-state-topology.md)** 🟢 — States isolados de `shared`, `staging` e `production`, com adoção sem recriação.
- **[ADR-029: Modern Task Runner (Just)](029-modern-task-runner-just.md)** 🟢 — Adoção do Just e PoeThePoet para orquestração unificada multiplataforma.

---

## 4. Decisões Históricas, Superadas, Consolidadas ou Rejeitadas

As decisões abaixo cumpriram papel fundamental nas fases iniciais da plataforma ou foram avaliadas e descartadas, sendo mantidas no repositório para preservação histórica:

| ADR Original | Status | Sucessor / Consolidador | Motivo da Evolução Arquitetural |
| :--- | :--- | :--- | :--- |
| **[ADR-006: Service Layer](006-service-layer.md)** | 🟡 Superada | **[ADR-030](030-rich-domain-model-service-layer.md)** | O modelo anêmico concentrava regras excessivas em services procedurais. Evoluiu para Rich Domain Model (Active Record Rico) com 3 níveis de validação. |
| **[ADR-008: Soft Delete Seletivo](008-soft-delete.md)** | ⚪ Rejeitada | *Nenhum* | Rejeitada no MVP em favor de hard delete direto com integridade referencial do banco para evitar complexidade de managers e filtros de exclusão lógica. |
| **[ADR-009: Multitenancy Base](009-multitenancy.md)** | 🟡 Superada | **[ADR-016](016-pragmatic-multi-tenancy.md)** | O isolamento original tratava casamentos (`WeddingOwnedMixin`) como unidade de tenant. Evoluiu para tenant corporativo (`Company` / `TenantModel`). |
| **[ADR-011: BaseModel full_clean](011-basemodel-save-full-clean.md)** | 🟢 Consolidada | **[ADR-030](030-rich-domain-model-service-layer.md)** | Incorporada formalmente como o Nível 2 (Invariantes de Domínio) na arquitetura Rich Domain Model. |
| **[ADR-015: (Proposta Legada)](README.md)** | ⚪ Descontinuada | *Nenhum* | Proposta preliminar descartada na fase inicial do projeto. Numeração preservada por integridade. |
| **[ADR-019: Tenant Validation](019-tenant-validation-service-layer.md)** | 🟡 Consolidada | **[ADR-016](016-pragmatic-multi-tenancy.md)** | O helper `validate_tenant_ownership` foi incorporado como o Pilar 4 do modelo pragmático da ADR-016. |
| **[ADR-028: Diátaxis & Notas Atômicas](028-diataxis-atomic-notes.md)** | 🟡 Emendada | **[ADR-030](030-rich-domain-model-service-layer.md)** (§ 3) | A cláusula de transclusões de código por número de linhas foi substituída por referências diretas a símbolos para mitigar code-drift. |

---

## 5. Diretrizes para Criação de Novas ADRs

Sempre que uma nova decisão arquitetural estrutural for adotada no projeto:
1. Criar novo arquivo em `docs/architecture/adr/` seguindo a sequência `XXX-nome-da-decisao.md`.
2. Incluir cabeçalho com Categoria, Status, Data, Decisor e Relações.
3. Se a nova decisão substituir, consolidar ou emendar uma ADR anterior, atualizar o status da ADR precedente com o respectivo banner de alerta e referenciá-la na tabela de decisões históricas acima.
4. Executar `just check-docs` (ou `uv run --project backend python scripts/validate_docs_links.py`) para certificar que nenhum link ou referência foi quebrado.
