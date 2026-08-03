# ADR-025: Adoção de Terraform e GitOps para Infraestrutura Multi-Cloud

> **Status:** Aceito
> **Data:** 1 de agosto de 2026
> **Decisores:** Time de Arquitetura & Plataforma
> **Relacionados:** [ADR-001](001-why-cloud-run.md) | [ADR-004](004-presigned-urls.md) | [ci-cd-pipeline-flow](../architecture/ci-cd-pipeline-flow.md)

---

## 1. Contexto e Problema

O **Wedding Management System** utiliza uma arquitetura multi-cloud desacoplada composta por:
- **Google Cloud Platform (GCP)**: Serviço Cloud Run v2 (Backend Django Ninja), Artifact Registry (Imagens OCI) e Workload Identity Federation (WIF).
- **Cloudflare**: Buckets R2 Storage para uploads de contratos/mídias em PDF com regras de CORS (ADR-004).
- **Vercel**: Hospedagem da SPA React (`wedding-web-app`) e Landing Page Astro (`wedding-landing`).
- **Neon DB**: Banco relacional Serverless PostgreSQL.

Anteriormente, o provisionamento desses serviços era realizado via consoles web ("Click-ops"), o que gerava riscos de inconsistência de configuração entre ambientes, ausência de rastreabilidade e dependência de chaves estáticas de longa duração.

---

## 2. Decisão

Decidimos adotar **Terraform (v1.5+)** com o modelo de automação **GitOps via GitHub Actions** para gerenciar declarativamente 100% da infraestrutura do projeto.

### Diretrizes de Arquitetura da Infraestrutura:
1. **Estrutura Modular (`terraform/`)**:
   - `main.tf`: Provedores (`google`, `cloudflare`, `vercel`, `github`) e Remote Backend no GCS (`wedding-management-tfstate`).
   - `gcp_iam.tf`: Workload Identity Federation (WIF) Pool, Provider e Service Account com permissões mínimas (Princípio do Menor Privilégio).
   - `gcp_cloud_run.tf`: Artifact Registry e serviço Cloud Run v2 com políticas de escalabilidade.
   - `cloudflare_r2.tf`: Bucket R2 e regras de CORS para suporte a Presigned URLs.
   - `vercel.tf`: Projetos Vercel e injeção automática de `VITE_API_URL`.
2. **Estratégia de Importação Sem Downtime**:
   - Uso de blocos `import {}` declarativos para incorporar recursos já existentes nos consoles sem destruição ou indisponibilidade.
3. **Pipeline GitOps (`terraform-ci.yml`)**:
   - `terraform plan` é executado em Pull Requests e os resultados são comentados automaticamente no PR.
   - `terraform apply` executa exclusivamente após o merge na branch `main` via autenticação WIF.

---

## 3. Consequências

### Positivas
- **Single Source of Truth**: O repositório Git passa a ser a única fonte da verdade para o estado da infraestrutura.
- **Rastreabilidade & Compliance**: Qualquer alteração na infra exige aprovação de Pull Request.
- **Injeção de Dependências Dinâmica**: A URL exportada do Cloud Run é propagada automaticamente para o frontend na Vercel via Terraform.
- **Segurança Reforçada**: Eliminação total de chaves e senhas estáticas de longa duração na CI/CD graças ao WIF.

### Negativas / Riscos Mitigados
- **Gestão de Estado**: O estado do Terraform contém metadados sensíveis; mitigado utilizando armazenamento criptografado no GCS com controle de acesso restrito.

---

## 4. Referências
- [ADR-001: Por que Google Cloud Run?](001-why-cloud-run.md)
- [ADR-004: Upload Direto via Presigned URLs no Cloudflare R2](004-presigned-urls.md)
- [Especificação de CI/CD](../architecture/ci-cd-pipeline-flow.md)
