# ADR-026: Estratégia de Branches, Ambientes (Staging/Produção) e GitOps Workflow

> **Status:** Aceito
> **Data:** 1 de agosto de 2026
> **Decisores:** Time de Arquitetura & Plataforma
> **Relacionados:** [ADR-001](001-why-cloud-run.md) | [ADR-025](025-terraform-iac-architecture.md) | [gitops-sprint-workflow](../../1-tutorials/gitops-sprint-workflow.md) | [ci-cd-pipeline-flow](../architecture/ci-cd-pipeline-flow.md)

---

## 1. Contexto e Problema

Com a evolução da plataforma e a necessidade de testar integrações complexas (como fluxos de autenticação JWT/OAuth, Presigned URLs no Cloudflare R2 e migrações no Neon DB) sem riscos à produção, o modelo antigo de deploys diretos a partir de branches individuais ou commits na `main` tornou-se arriscado.

Especificamente:
- Falhas de variáveis de ambiente de autenticação (Callback URIs e segredos de API) só eram descobertas em produção.
- Ausência de um ambiente de homologação (Staging) espelhado e privado para validação durante o ciclo de Sprints.
- Necessidade de um fluxo estruturado para correções urgentes (Hotfixes) sem interromper as tarefas em andamento na Sprint.

---

## 2. Decisão

Adotamos o **GitHub Flow estendido com Homologação (Staging)** orientado a Sprints, estruturado em duas branches permanentes e duas categorias de branches temporárias.

### 2.1 Modelo de Branches
1. **`main` (Produção)**: Branch imutável de código estável. Reflete exatamente o sistema ativo em produção (`wedding-api`, `wedding-web-app`).
2. **`develop` (Homologação / Staging)**: Branch de integração contínua da Sprint. Reflete o ambiente de testes privado (`wedding-api-staging`, `wedding-web-app-staging`).
3. **`feature/*`**: Branches de desenvolvimento de tarefas da Sprint criadas a partir da `develop`.
4. **`hotfix/*`**: Branches de correções emergenciais em produção criadas a partir da `main`.

### 2.2 Automação de Deploys e Pipelines (GitOps)
- **Pull Request ➡️ `develop`**: Executa linters, tipagem estrita, suíte de testes unitários (`pytest`, `vitest`) e sincronização de contratos OpenAPI/Orval.
- **Merge ➡️ `develop`**: Aciona o deploy automático no **Ambiente de Homologação (Staging)** de forma 100% isolada e protegida.
- **Pull Request `develop` ➡️ `main` (Fim da Sprint)**: Executa o `terraform plan`, postando o diff no PR, e roda a suíte de testes de regressão E2E (Playwright).
- **Merge ➡️ `main`**: Aciona o deploy automático em **Produção**.

---

## 3. Consequências

### Positivas
- **Zero Surpresas de Variáveis em Produção**: Todas as URLs de callback, CORS e segredos de OAuth2 são validadas em Staging antes do lançamento.
- **Ambiente Privado de Homologação**: Validação de fluxos de autenticação e mídias R2 em nuvem sem expor o sistema a buscadores ou ao público.
- **Previsibilidade nas Sprints**: Lançamentos em blocos organizados no fim da Sprint via PR `develop ➡️ main`.
- **Hotfixes Seguros**: Correções urgentes podem ser enviadas diretamente para a `main` e sincronizadas na `develop` em minutos.

### Negativas / Riscos Mitigados
- Requer disciplina na criação de branches; mitigado via regras de proteção de branch (*Branch Protection Rules*) no GitHub.

---

## 4. Referências
- [ADR-025: Adoção de Terraform e GitOps](025-terraform-iac-architecture.md)
- [Tutorial: Fluxo de Trabalho por Sprints](../../1-tutorials/gitops-sprint-workflow.md)
- [Especificação de CI/CD](../architecture/ci-cd-pipeline-flow.md)
