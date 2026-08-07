# 🏛️ Architecture Decision Records (ADRs)

> **Módulo:** [system-overview](../architecture/system-overview.md) | [docs-portal](../../README.md)
> **Escopo:** Catálogo Oficial de Decisões Arquiteturais e Registros de Trade-offs do Projeto

---

## 1. Visão Geral

Esta pasta reúne todos os **Architecture Decision Records (ADRs)** do Wedding Management System. Cada ADR documenta uma decisão estrutural relevante, seu contexto, alternativas consideradas e as consequências arquiteturais adotadas.

> ℹ️ **Nota de Numeração Imutável:** A numeração das ADRs é mantida estritamente imutável para preservar a rastreabilidade histórica no código-fonte, comentários de classe e mensagens de commit do Git. A identificação `ADR-015` refere-se a uma proposta descontinuada na fase inicial do projeto, mantendo-se a sequência oficial das 27 ADRs ativas.

---

## 2. Índice de Decisões Arquiteturais (001 a 027)

### ☁️ Infraestrutura & Cloud Storage
- **[ADR-001: Cloud Run](001-why-cloud-run.md)** — Hospedagem Serverless do Backend Django Ninja no GCP Cloud Run.
- **[ADR-002: Neon PostgreSQL](002-why-neon.md)** — Banco de dados PostgreSQL Serverless com suporte a Database Branching.
- **[ADR-003: Cloudflare R2](003-why-r2.md)** — Armazenamento de PDFs e anexos com custo zero de transferência (egress).
- **[ADR-004: Presigned URLs](004-presigned-urls.md)** — Upload direto e seguro de contratos para o R2 sem sobrecarregar o backend.
- **[ADR-005: Cloud Scheduler & OIDC](005-oidc-scheduler.md)** — Automação de tarefas cron via requisições autenticadas por OIDC Service Accounts.
- **[ADR-020: StorageService Abstraction](020-storage-service-abstraction.md)** — Camada de abstração e injeção de dependência de serviço de storage.
- **[ADR-025: Terraform & GitOps](025-terraform-iac-architecture.md)** — Infraestrutura como código (IaC), ownership e automação GitOps multi-cloud.
- **[ADR-026: Estratégia de Branches & Staging](026-gitops-branching-and-deployment-strategy.md)** — Modelo de branches (`main`/`develop`), homologação privada e ciclo por Sprints.
- **[ADR-027: Topologia dos States Terraform](027-terraform-state-topology.md)** — States isolados de `shared`, `staging` e `production`, com adoção sem recriação.

---

### 🛡️ Arquitetura Backend, Segurança & Integridade
- **[ADR-006: Service Layer Pattern](006-service-layer.md)** — Isolamento estrito de regras de negócio na camada de serviços (sem lógica no controller).
- **[ADR-007: Hybrid Keys](007-hybrid-keys.md)** — Uso de chaves híbridas (BigInt interno em relacionamentos e UUID v4 público na API).
- **[ADR-008: Soft Delete Strategy](008-soft-delete.md)** — Estratégia de exclusão lógica versus remoção física em entidades financeiras.
- **[ADR-009: Multi-tenancy Strategy](009-multitenancy.md)** — Isolamento de dados multi-tenant baseado em coluna de pertencimento (`Company`).
- **[ADR-010: Tolerância Zero](010-tolerance-zero.md)** — Princípio contábil da divisão exata de parcelas sem perda de centavos no arredondamento.
- **[ADR-011: BaseModel full_clean()](011-basemodel-save-full-clean.md)** — Execução automática da validação `full_clean()` durante a escrita no banco.
- **[ADR-013: Django Ninja API](013-migrate-drf-to-ninja.md)** — Substituição do Django REST Framework (DRF) pelo Django Ninja por alta performance e tipagem Pydantic.
- **[ADR-014: Tipagem Estática Estrita (mypy)](014-adocao-tipagem-estatica-mypy.md)** — Adoção de checagem estática de tipos no backend Python.
- **[ADR-016: Pragmatic Multi-tenancy](016-pragmatic-multi-tenancy.md)** — Validação pragmática de multi-tenancy na camada de serviços.
- **[ADR-017: Async Task Infrastructure](017-async-task-infrastructure.md)** — Infraestrutura de tarefas assíncronas e agendadas.
- **[ADR-019: Tenant Validation in Services](019-tenant-validation-service-layer.md)** — Recebimento obrigatório do parâmetro `company` em métodos de serviço.
- **[ADR-022: Static Routes Optimization](022-static-routes-for-performance.md)** — Priorização de rotas estáticas para otimização de performance de resposta da API.
- **[ADR-023: Desacoplamento de Módulos](023-desacoplamento-modulos-scheduler-finances-weddings.md)** — Desacoplamento entre os domínios Scheduler, Finances e Weddings.

---

### 🎨 Arquitetura Frontend & Qualidade
- **[ADR-012: Orval Contract-Driven API](012-orval-contract-driven-frontend.md)** — Geração automática de hooks React Query e tipos TypeScript a partir do OpenAPI schema.
- **[ADR-018: Playwright E2E Testing](018-playwright-e2e-testing.md)** — Adoção do Playwright para testes de integração end-to-end do frontend.
- **[ADR-021: Commenting & Docstring Standards](021-padrao-comentarios-docstrings.md)** — Padrão de comentários e Google Style docstrings (escritos em PT-BR para explicações de negócio).
- **[ADR-024: Smart/Dumb Components Pattern](024-padrao-smart-dumb-desacoplamento-componentes-frontend.md)** — Separação clara entre componentes de container síncronos e componentes visuais desacoplados.

---

## 3. Diretrizes para Criação de Novas ADRs

Sempre que uma nova decisão arquitetural estrutural for adotada no projeto, um novo arquivo deve ser criado nesta pasta seguindo o padrão de nomenclatura `XXX-nome-da-decisao.md` e catalogado no índice acima.
