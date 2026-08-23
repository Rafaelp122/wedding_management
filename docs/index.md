# Wedding Management System — Documentação Técnica

Bem-vindo à documentação técnica oficial da plataforma **Wedding Management System**, um SaaS multi-tenant desenvolvido para assessores e casais gerenciarem orçamentos, contratos, fornecedores e cronogramas de casamentos.

---

## Navegação Rápida

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Onboarding e Primeiros Passos**

    ---

    Aprenda a subir o ambiente local completo em Docker, rodar migrações e criar suas primeiras features.

    [:octicons-arrow-right-24: Ir para Onboarding](onboarding/onboarding-quickstart.md)

-   :material-book-open-variant:{ .lg .middle } **Guias de Desenvolvimento**

    ---

    Receitas práticas passo a passo para Frontend (React, Orval, Zod) e Backend (Django Ninja, Pytest).

    [:octicons-arrow-right-24: Ver Guias Práticos](guides/backend/use-core-services.md)

-   :material-sitemap:{ .lg .middle } **Arquitetura e Regras de Negócio**

    ---

    Entenda a estratégia de Multi-Tenancy, o padrão Service Layer e o cálculo de Tolerância Zero.

    [:octicons-arrow-right-24: Explorar Arquitetura](architecture/index.md)

-   :material-code-json:{ .lg .middle } **Referência Técnica e APIs**

    ---

    Contratos OpenAPI, schemas de banco de dados, especificações HCL do Terraform e MOC de testes.

    [:octicons-arrow-right-24: Ver Referência Técnica](reference/api/index.md)

</div>

---

## Stack Tecnológica

| Camada | Tecnologia Principal |
| :--- | :--- |
| **Backend** | Python 3.12, Django 5.2, Django Ninja (Pydantic v2), PostgreSQL (Neon) |
| **Frontend** | React 19, TypeScript, Tailwind CSS v4, shadcn/ui, TanStack Query, Orval |
| **Infraestrutura** | Serverless no GCP Cloud Run, Cloudflare R2 (Storage), Terraform (IaC) |
| **CI/CD & Qualidade** | GitHub Actions, Pytest, Vitest, Playwright E2E, Ruff, mypy |
