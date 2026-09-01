# Hub de Guias, Tutoriais & Onboarding

> **Categoria:** Guias Práticos & Tutoriais (Diátaxis: How-To & Tutorials)
> **Relacionados:** [Quickstart do Ambiente](../onboarding/onboarding-quickstart.md) · [System Design Fullstack](../architecture/index.md) · [Referência Técnica](../reference/index.md) · [Padrões de Qualidade](../reference/architecture-standards/index.md)

<p class="mdx-hero__subtitle" style="font-size: 1.15rem; font-weight: 500; color: var(--md-default-fg-color--light); margin-top: -0.5rem; margin-bottom: 1.5rem;">
Trilhas guiadas passo a passo para integração de novos engenheiros, receitas de desenvolvimento fullstack (Django Ninja & React 19) e playbooks operacionais de troubleshooting.
</p>

<p align="left" style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 2rem;">
  <span class="md-tag" style="background-color: #3776AB; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Quickstart Local</span>
  <span class="md-tag" style="background-color: #087EA4; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Django Ninja</span>
  <span class="md-tag" style="background-color: #61DAFB; color: #09090B; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">React 19 & Orval</span>
  <span class="md-tag" style="background-color: #E92063; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Hook Form + Zod</span>
  <span class="md-tag" style="background-color: #F59E0B; color: #09090B; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">MSW & RTL</span>
  <span class="md-tag" style="background-color: #2EAD33; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Pytest & Factories</span>
  <span class="md-tag" style="background-color: #2E7D32; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Playwright E2E</span>
  <span class="md-tag" style="background-color: #DC2626; color: white; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">Ops Troubleshooting</span>
</p>

[:material-rocket-launch: Quickstart Onboarding](../onboarding/onboarding-quickstart.md){ .md-button .md-button--primary }
[:material-server: Playbooks Backend](backend/use-core-services.md){ .md-button }
[:material-react: Playbooks Frontend](frontend/generate-orval-client.md){ .md-button }
[:material-wrench: Troubleshooting Ops](ops-troubleshooting/db-connection-locks.md){ .md-button }

---

## Trilhas de Aprendizado & Playbooks de Desenvolvimento

Navegue pelos guias e tutoriais práticos organizados por foco de atuação:

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Onboarding & Primeiros Passos**

    ---

    Trilhas passo a passo para novos desenvolvedores configurarem a máquina local, criarem sua primeira feature e entenderem o ciclo de entrega contínua.

    [:octicons-arrow-right-24: Quickstart do Ambiente Local](../onboarding/onboarding-quickstart.md)
    [:octicons-arrow-right-24: Criando Endpoints no Backend](../onboarding/backend-first-feature.md)
    [:octicons-arrow-right-24: Criando Telas no Frontend](../onboarding/frontend-first-feature.md)
    [:octicons-arrow-right-24: GitOps & Fluxo por Sprints](../onboarding/gitops-sprint-workflow.md)

-   :material-language-python:{ .lg .middle } **Backend & APIs (Django Ninja)**

    ---

    Playbooks operacionais para o Service Layer, queries otimizadas em selectors, notificações em background, tarefas cron e testes automatizados.

    [:octicons-arrow-right-24: Padrão Service Layer](backend/use-core-services.md)
    [:octicons-arrow-right-24: Query Selectors Customizados](backend/create-query-selectors.md)
    [:octicons-arrow-right-24: Suíte Pytest & Factories](backend/run-pytest-suite.md)
    [:octicons-arrow-right-24: Notificações In-App](backend/send-in-app-notifications.md)
    [:octicons-arrow-right-24: Background Tasks](backend/create-background-tasks.md)
    [:octicons-arrow-right-24: Tarefas Cron no Cloud Scheduler](backend/register-cron-tasks.md)
    [:octicons-arrow-right-24: Lógica de Parcelas Atrasadas](backend/mark-overdue-installments.md)
    [:octicons-arrow-right-24: População de Banco (Seed)](backend/seed-database.md)

-   :material-react:{ .lg .middle } **Frontend SPA (React 19 & Orval)**

    ---

    Receitas de implementação para sincronização de contratos OpenAPI, formulários com validação Zod, mocks MSW e testes E2E.

    [:octicons-arrow-right-24: Geração de Cliente Orval](frontend/generate-orval-client.md)
    [:octicons-arrow-right-24: Formulários com Hook Form + Zod](frontend/create-hook-form-zod.md)
    [:octicons-arrow-right-24: Uso do Design System](frontend/use-design-md-system.md)
    [:octicons-arrow-right-24: Mocks de API com MSW](frontend/msw-testing-patterns.md)
    [:octicons-arrow-right-24: Testes E2E com Playwright](frontend/run-playwright-e2e.md)

-   :material-server-network:{ .lg .middle } **Ambiente Local & Banco de Dados**

    ---

    Tutoriais para setup do ambiente híbrido (Docker Compose + Host local com UV e Pnpm) e boas práticas no ciclo de vida de migrações.

    [:octicons-arrow-right-24: Hub do Ambiente Local](dev-environment/index.md)
    [:octicons-arrow-right-24: Setup Local Completo](dev-environment/setup-local-environment.md)
    [:octicons-arrow-right-24: Guia de Migrações do Banco](dev-environment/database-migrations.md)

-   :material-alert-decagram:{ .lg .middle } **Operações & Troubleshooting**

    ---

    Playbooks de resolução rápida de incidentes para locks de conexão no PostgreSQL Neon, falhas de upload no Cloudflare R2 e provisionamento Terraform.

    [:octicons-arrow-right-24: Diagnóstico de DB Connection Locks](ops-troubleshooting/db-connection-locks.md)
    [:octicons-arrow-right-24: Resolução de Falhas de Upload R2](ops-troubleshooting/r2-upload-failures.md)
    [:octicons-arrow-right-24: Onboarding de Serviços Terraform](ops-troubleshooting/terraform-service-onboarding.md)

-   :material-book-open-page-variant:{ .lg .middle } **Governança & Documentação**

    ---

    Padrões e tutoriais para criação e manutenção contínua da documentação técnica no padrão Diátaxis e notas atômicas.

    [:octicons-arrow-right-24: Hub de Guias de Documentação](documentation/index.md)
    [:octicons-arrow-right-24: Como Escrever e Atualizar Docs](documentation/write-and-update-docs.md)

</div>

---

## Cheatsheet de Comandos Essenciais do Desenvolvedor

| Ação | Comando Makefile | Descrição Operacional |
| :--- | :--- | :--- |
| **Setup do Ambiente** | `make setup` | Cria `.env`, sobe containers Docker, aplica migrações e cria o superusuário. |
| **Subir Aplicações** | `make up` / `make dev` | Sobe o banco e backend Django no Docker com streaming de logs. |
| **Frontend SPA** | `make frontend-dev` | Inicia o servidor Vite local no host na porta `5173`. |
| **Landing Page** | `make landing-dev` | Inicia o servidor Astro local no host na porta `4321`. |
| **Sincronizar API** | `make sync-api` | Exporta `openapi.json` do Django Ninja e regenera hooks Orval e tipos Zod. |
| **Testes Backend** | `make test` | Executa a suíte Pytest dentro do container backend. |
| **Testes Frontend** | `make frontend-test` | Executa a suíte Vitest com RTL e mocks MSW no frontend. |
| **Testes E2E** | `make frontend-e2e` | Reseta o banco de testes com seed e roda a suíte Playwright. |
| **Gate Local de CI** | `make check-ci` | Executa todos os testes, linters e checagens estritas do repositório. |
| **Documentação Local**| `make docs-dev` | Inicia o servidor MkDocs com live-reload na porta `8001`. |
