# ADR-025: Adoção de Terraform e GitOps para Infraestrutura Multi-Cloud

> **Status:** Aceito
> **Data:** 1 de agosto de 2026
> **Decisores:** Time de Arquitetura & Plataforma
> **Relacionados:** [ADR-001](001-why-cloud-run.md) | [ADR-004](004-presigned-urls.md) | [ADR-027](027-terraform-state-topology.md) | [ci-cd-pipeline-flow](../architecture/ci-cd-pipeline-flow.md)

---

## 1. Contexto e Problema

O Wedding Management System usa GCP Cloud Run e Artifact Registry, Cloudflare R2, Vercel e Neon PostgreSQL. Parte dessa infraestrutura já existia antes da adoção do Terraform e ainda precisava ser inventariada e importada sem recriação ou indisponibilidade.

Um único root com `production.tfvars` e `staging.tfvars` também fazia recursos globais e ambientais compartilharem os mesmos addresses e state. Trocar o arquivo de variáveis não cria isolamento de state e pode fazer um plano de staging propor alterações em produção.

---

## 2. Decisão

Adotamos Terraform 1.5+ para os recursos explicitamente declarados, com ownership único e três roots remotos:

| Root | Ownership | Prefixo do backend |
|:---|:---|:---|
| `shared` | Bucket de state após bootstrap/import, Artifact Registry, WIF, Service Account/IAM e projetos Vercel. | `terraform/shared` |
| `production` | Cloud Run/IAM público, bucket R2 e variáveis Vercel do target `production`. | `terraform/production` |
| `staging` | Cloud Run/IAM público, bucket R2 e variáveis Vercel do target `preview`. | `terraform/staging` |

Cada recurso pertence a exatamente um state. Os roots ambientais consomem apenas outputs e IDs do root `shared`, sem duplicar ownership. Workspaces não substituem essa separação.

### 2.1 Limites de ownership

- **Terraform:** provisiona e mantém os recursos declarados na tabela anterior.
- **CD da aplicação:** publica a imagem, executa migrations e atualiza imagem, secrets e variáveis de runtime no Cloud Run; esses campos não são disputados pelo Terraform.
- **Externo/manual:** dados e branches Neon, valores do Secret Manager, credenciais e configurações que não possuem resource Terraform declarado.

O repositório é fonte da configuração desejada somente dentro desse escopo. Não adotamos a premissa de que 100% da infraestrutura ou dos valores secretos seja gerenciada por Terraform.

### 2.2 Adoção dos recursos existentes

Antes de liberar qualquer `apply`, cada recurso preexistente deve ser inventariado e importado diretamente no state proprietário. Os IDs vêm dos providers, não de nomes presumidos em comentários.

Após os imports, cada root deve produzir um plano convergente, sem criação, substituição ou remoção inesperada. O Artifact Registry `wedding-management-repo`, criado durante o bootstrap do CD, pertence ao root `shared` e também deve ser importado.

### 2.3 Automação GitOps

- Pull requests executam `fmt`, `init -backend=false` e `validate` em todos os roots, sem OIDC e sem acesso ao state remoto.
- Pushes em `develop` podem gerar os planos dos roots `shared` e `staging`; nenhum deles é aplicado automaticamente.
- Pushes em `main` geram os planos de `shared` e `production` e podem aplicá-los, nessa ordem, apenas quando a repository variable `TERRAFORM_PRODUCTION_APPLY_ENABLED` for exatamente `true`.
- O opt-in de produção permanece ausente ou `false` durante inventário, imports e revisão dos planos.
- Operações remotas são serializadas para evitar disputa de lock, sem misturar os prefixes dos ambientes.

Durante a adoção, o provider WIF preserva a condição ativa que aceita somente tokens do repositório emitidos para `main` ou `develop`. Workflows de pull request não representam a Service Account de deploy. A restrição adicional por workflow será tratada depois da convergência dos states.

---

## 3. Consequências

### Positivas

- Ownership único por recurso e isolamento entre shared, staging e produção.
- Planos de staging não alteram recursos de produção, e vice-versa.
- URLs Vercel são gerenciadas por target: `production` aponta para `wedding-backend`; `preview`, para `wedding-backend-staging`.
- Infraestrutura existente pode ser adotada sem downtime quando inventário, imports e planos convergentes são respeitados.

### Negativas e riscos

- State e planos podem conter metadados sensíveis e exigem acesso restrito, versionamento e backups privados.
- Bootstrap e imports dependem de inventário manual e credenciais administrativas temporárias.
- Dependências entre roots exigem outputs shared estáveis e ordem explícita de operação.
- `apply` de produção continua bloqueado até aprovação manual após a convergência dos três states.

---

## 4. Referências

- [ADR-001: Por que Google Cloud Run?](001-why-cloud-run.md)
- [ADR-004: Upload Direto via Presigned URLs no Cloudflare R2](004-presigned-urls.md)
- [ADR-026: Estratégia de Branches e Staging](026-gitops-branching-and-deployment-strategy.md)
- [ADR-027: Topologia e Ownership dos States](027-terraform-state-topology.md)
- [Especificação de CI/CD](../architecture/ci-cd-pipeline-flow.md)
- [Issue #352: adotar recursos e isolar states](https://github.com/Rafaelp122/wedding_management/issues/352)
