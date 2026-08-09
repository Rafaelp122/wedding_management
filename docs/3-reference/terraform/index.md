# 🏗️ Especificações Técnicas de Módulos Terraform (MOC)

> **Módulo:** [architecture-standards](../architecture-standards/index.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)
> **Camada:** Infraestrutura IaC (`terraform/modules/`)

---

## Visão Geral

As especificações de infraestrutura IaC do **Wedding Management System** definem o contrato de desenvolvimento dos módulos HCL reutilizáveis sob `terraform/modules/`.

Cada módulo segue um **contrato padrão de 5 arquivos**:
1. `versions.tf`: Versão travada do Terraform (`= 1.7.5`) e provedores.
2. `variables.tf`: Entradas tipadas com `validation {}`.
3. `main.tf`: Recursos HCL do provedor com lifecycles de segurança.
4. `outputs.tf`: Atributos expostos com descrição em PT-BR acentuada.
5. `tests/unit_test.tftest.hcl`: Suíte de testes declarativos nativos em `command = plan` (consulte [terraform-testing-spec](../testing/terraform-testing-spec.md)).

---

## 📌 Especificações Atômicas de Módulos

- ☁️ **[cloud-run-service-module.md](cloud-run-service-module.md)** — Especificação técnica do módulo GCP Cloud Run v2, Secret Manager e bindings IAM (`terraform/modules/gcp/cloud-run-service/`).
