# ADR-026: Estratégia de Branches, Ambientes e GitOps Workflow

> **Status:** Aceito
> **Data:** 1 de agosto de 2026
> **Decisores:** Time de Arquitetura & Plataforma
> **Relacionados:** [ADR-001](001-why-cloud-run.md) | [ADR-025](025-terraform-iac-architecture.md) | [gitops-sprint-workflow](../../1-tutorials/gitops-sprint-workflow.md) | [ci-cd-pipeline-flow](../architecture/ci-cd-pipeline-flow.md)

---

## 1. Contexto e Problema

Integrações como OAuth, uploads R2 e migrations Neon precisam ser validadas em um ambiente persistente antes da promoção para produção. Deploys diretos de branches temporárias não oferecem uma referência estável para URLs, dados e configuração de terceiros.

Também é necessário distinguir validação de pull request, deploy da aplicação e mudanças declarativas de infraestrutura. Aprovar código não autoriza automaticamente acesso OIDC, state remoto ou `terraform apply`.

---

## 2. Decisão

Adotamos GitHub Flow estendido com duas branches permanentes:

| Branch | Papel | Ambiente |
|:---|:---|:---|
| `main` | Código estável | Production: Cloud Run `wedding-backend` e Vercel Production. |
| `develop` | Integração da Sprint | Staging fixo: Cloud Run `wedding-backend-staging` e target Vercel Preview. |
| `feature/*` | Tarefas iniciadas em `develop` | Somente validação em pull request. |
| `hotfix/*` | Correções iniciadas em `main` | Somente validação até o merge em `main`. |

O GitHub Environment chamado `Preview` representa o staging fixo associado a `develop`. Ele não é um ambiente full-stack efêmero por pull request. O nome do Environment, por si só, não implica regras de aprovação ou restrição de branch; essas políticas são configurações explícitas do GitHub.

### 2.1 Pull requests

PRs para `develop` ou `main` executam lint, tipagem, testes, builds, contratos e E2E conforme os caminhos alterados. Mudanças Terraform executam apenas validação local com `init -backend=false`.

Pull requests não fazem deploy, não recebem OIDC, não acessam state remoto e não publicam comentário de `terraform plan`.

### 2.2 Push em `develop`

Após sucesso da CI, o CD atualiza os componentes alterados no staging fixo. O backend usa `wedding-backend-staging`, banco/secrets próprios e configuração do target Vercel Preview.

Separadamente, a pipeline Terraform calcula os planos dos roots/states `shared` e `staging`. Ambos permanecem plan-only e nunca são aplicados automaticamente.

### 2.3 Push em `main`

Após sucesso da CI, o CD atualiza os componentes alterados em Production. O backend usa `wedding-backend`, e frontend/landing usam os targets Vercel Production.

Mudanças Terraform planejam os roots/states `shared` e `production`. Os applies exigem `TERRAFORM_PRODUCTION_APPLY_ENABLED == 'true'`; o padrão ausente ou `false` mantém a operação bloqueada. A habilitação ocorre fora do PR de código, após inventário, imports, planos convergentes e aprovação manual.

Recursos globais usados pelos dois ambientes pertencem ao root/state `shared`, conforme [ADR-025](025-terraform-iac-architecture.md).

---

## 3. Consequências

### Positivas

- Staging oferece URLs e recursos persistentes para homologação antes da promoção.
- Pull requests permanecem sem credenciais de deploy ou acesso a state.
- States ambientais separados impedem que um plano de staging altere produção.
- Hotfixes podem seguir diretamente para `main` e depois ser sincronizados em `develop`.

### Negativas e riscos

- Staging só representa produção quando banco, R2, OAuth, CORS e targets Vercel estão configurados e validados separadamente.
- O serviço Cloud Run pode ser público para atender o frontend; privacidade e proteção não devem ser inferidas do nome do ambiente.
- O fluxo exige disciplina de branches e políticas explícitas no GitHub para branches e Environments.
- O apply de produção depende de opt-in e aprovação operacional fora do merge de código.

---

## 4. Referências

- [ADR-025: Adoção de Terraform e GitOps](025-terraform-iac-architecture.md)
- [Tutorial: Fluxo de Trabalho por Sprints](../../1-tutorials/gitops-sprint-workflow.md)
- [Especificação de CI/CD](../architecture/ci-cd-pipeline-flow.md)
