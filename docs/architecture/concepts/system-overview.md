# Arquitetura do Sistema: Visão Geral (System Overview)

> **Módulo:** [system-overview](system-overview.md)
> **Relacionados:** [multi-tenancy-strategy](multi-tenancy-strategy.md) | [service-layer-pattern](service-layer-pattern.md) | [smart-dumb-components](smart-dumb-components.md) | [auth-jwt-flow](auth-jwt-flow.md) | [landing-page-spec](../../reference/frontend/landing-page-spec.md)

---

## Visão Geral da Arquitetura Fullstack

O **Wedding Management System** é uma plataforma multi-tenant SaaS concebida para assessores de eventos e noivos gerenciarem orçamentos, logística de contratos, fornecedores e cronogramas de casamentos. O ecossistema é composto por três aplicações integradas:

1. **Landing Page Comercial (`landing/`):** Portal público em **Astro 7** com ilhas interativas em **React 19** e **Tailwind CSS v4** para conversão de novos usuários e SEO.
2. **Frontend SPA (`frontend/`):** Single Page Application em **React 19** com **Vite**, **TanStack Query** e **shadcn/ui** para operações autenticadas de assessores e casais.
3. **Backend REST API (`backend/`):** API em **Python 3.12+** com **Django 6.0 LTS** e **Django Ninja**, operando sob o padrão **Service Layer (CQRS)** e banco **PostgreSQL Neon**.

```mermaid
graph TD
    subgraph Clients ["Camada de Apresentação (Frontend Clients)"]
        Landing["Landing Page Comercial<br/>(Astro 7 + Tailwind v4 + React Islands)"]
        SPA["Frontend SPA Autenticado<br/>(React 19 + TanStack Query + Orval)"]
    end

    subgraph BackendGateway ["Gateway & Backend (Django Ninja)"]
        API["Django Ninja REST API<br/>(Django 6.0 + Pydantic v2)"]
        Services["Service Layer (CQRS)<br/>(@transaction.atomic)"]
        Selectors["Query Selectors<br/>(TenantQuerySet Isolation)"]
    end

    subgraph CloudInfra ["Persistência & Nuvem"]
        DB[("PostgreSQL Neon Serverless<br/>(Multi-Tenant Column Isolation)")]
        R2[("Cloudflare R2 Storage<br/>(Presigned S3 API Uploads)")]
        Scheduler["Cloud Scheduler<br/>(OIDC Cron Tasks)"]
    end

    Landing -. "Conversão / Redirecionamento" .-> SPA
    SPA -->|HTTPS / REST JSON (JWT)| API
    API --> Services
    API --> Selectors
    Services --> DB
    Services --> R2
    Selectors --> DB
    Scheduler -->|OIDC Webhook| API
```

---

## Pilares Tecnológicos & Versões Sincronizadas

| Camada | Tecnologia Principal | Versão Exata | Função Principal |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | Python + Django + Django Ninja | `Python >=3.12`, `Django >=6.0.8`, `Ninja >=1.6.2` | API REST fortemente tipada com schemas Pydantic v2 e sem DRF. |
| **Arquitetura Backend** | Service Layer (CQRS) | Padrão Nativo | Endpoints em `api.py` nunca contêm lógica de negócio; chamam `services.py`. |
| **Isolamento de Dados** | Multi-Tenancy Pragmático | `psycopg >=3.3.4` | `Company` é o tenant root; models herdam de `TenantModel` (ADR-009, ADR-016). |
| **Frontend SPA** | React + Vite + TypeScript | `React ^19.2.8`, `Vite ^8.2.1`, `TS ^7.0` | SPA de alta performance com Tailwind CSS v4 e componentes shadcn/ui. |
| **Landing Page** | Astro + React Islands | `Astro ^7.1.1`, `@astrojs/react ^6.0.2` | Vitrine comercial estática com carregamento instantâneo e SEO otimizado. |
| **Contratos e API Client**| Orval + TanStack Query | `Orval ^8.24.0`, `Query ^5.101.4` | Geração automática de hooks TypeScript e tipos a partir do OpenAPI 3.1. |
| **Formulários** | `react-hook-form` + `zod` | `RHF ^7.85.0`, `Zod ^4.4.3` | Validação de schemas no cliente alinhada com as mensagens da API. |
| **Tarefas & Workers** | Huey + Redis/Valkey | `huey >=2.5.0`, `redis >=5.0.0` | Filas assíncronas e agendamento de tarefas em background. |
| **Armazenamento de Arquivos**| Cloudflare R2 (S3 API) | `django-storages >=1.14.6`, `boto3 >=1.43` | Armazenamento de contratos PDF com custo zero de egresso (ADR-003, ADR-004). |
| **Infraestrutura Serverless**| Google Cloud Run + Terraform | Terraform `>=1.10`, Cloud Run | Hospedagem serverless com escala a zero e infraestrutura como código declarativa. |
