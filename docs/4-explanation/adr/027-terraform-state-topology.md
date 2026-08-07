# ADR-027: Topologia e Ownership dos States Terraform

> **Status:** Aceito
> **Data:** 6 de agosto de 2026
> **Relacionados:** [ADR-025](025-terraform-iac-architecture.md) | [ADR-026](026-gitops-branching-and-deployment-strategy.md) | [runbook de adoção](../../2-how-to/ops-troubleshooting/terraform-state-adoption.md)

## Contexto

O root Terraform original misturava recursos globais, staging e produção no mesmo prefixo GCS. Como os arquivos `staging.tfvars` e `production.tfvars` usavam os mesmos endereços Terraform para objetos físicos diferentes, um plano de staging podia propor a substituição de recursos de produção.

Parte da infraestrutura também já existia fora do state: Cloud Run, Artifact Registry, WIF, IAM, Secret Manager, Vercel e Cloudflare R2. Aplicar antes da adoção poderia recriar ou remover recursos ativos.

## Decisão

Adotamos três roots e prefixes independentes:

| Root | Prefixo | Ownership |
|:---|:---|:---|
| `shared` | `terraform/shared` | Bucket de state, Artifact Registry, WIF, deployer IAM e projetos Vercel |
| `staging` | `terraform/staging` | Cloud Run/IAM, secrets/IAM, R2 e variável Vercel de staging |
| `production` | `terraform/production` | Cloud Run/IAM, secrets/IAM, R2 e variável Vercel de produção |

Não usamos workspaces para representar ambientes. Cada objeto remoto pertence a um único state ativo.

### Limite entre Terraform e CD

Terraform gerencia configuração estável: existência dos serviços, capacidade, rede, IAM, buckets, containers de secrets e projetos. O CD gerencia cada release: imagem por SHA, env vars, referências de versões, migrations, revisões, tráfego e deployments Vercel.

Valores de secrets, objetos R2, imagens, projetos Neon e connection strings permanecem externos ao Terraform. Os values do Secret Manager nunca entram no state.

### Adoção

Os recursos existentes são importados diretamente no state proprietário. Durante a adoção:

1. o prefixo legado fica congelado;
2. cada configuração reproduz primeiro o recurso real;
3. somente planos contendo importações são aplicados;
4. qualquer `create`, `update`, `replace` ou `destroy` bloqueia a operação;
5. o apply automático continua desabilitado até os três planos convergirem.

Hardening e redução de IAM não são misturados com imports. Essas alterações ocorrem em planos posteriores e revisáveis.

## Consequências

### Positivas

- Staging não pode alterar recursos de produção pelo compartilhamento de endereços.
- Ownership entre Terraform e CD fica explícito.
- Imports e rollback podem ser executados por domínio.
- Novos serviços permanentes, como filas Cloud Tasks, podem ser adicionados ao state correto.

### Negativas

- Há pequena duplicação entre os roots ambientais.
- Mudanças compartilhadas e ambientais exigem planos separados.
- A adoção inicial requer inventário e imports manuais controlados.

## Restrições Operacionais

- Não usar `state push -force`, `init -force-copy`, `force-unlock` ou `-lock=false`.
- Não publicar state ou planos como artifacts.
- Não habilitar `TERRAFORM_PRODUCTION_APPLY_ENABLED` antes da convergência.
- Manter versionamento e soft delete no bucket GCS.
