# MOC de Domínio: Logistics (Fornecedores e Contratos)

> **Hub de Domínio:** [logistics-domain](logistics-domain.md) | [system-overview](../architecture/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/logistics/` & `frontend/src/features/logistics/`

---

## Visão Geral do Domínio

O domínio de **Logistics** é responsável pela gestão do catálogo de fornecedores da assessoria, controle de contratos assinados (com suporte a aditivos) e controle dos itens/serviços contratados para cada casamento.

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/logistics/`)
- **Modelos de Dados:**
  - [supplier-model](../../3-reference/models/logistics/supplier-model.md): Cadastro de fornecedores com validação de CNPJ.
  - [contract-model](../../3-reference/models/logistics/contract-model.md): Contratos com suporte a PDF e hierarquia de aditivos.
  - [item-model](../../3-reference/models/logistics/item-model.md): Itens contratados por evento.
- **Service Layer:** `contract_service.py`, `supplier_service.py`, `item_service.py`.

### 2. Camada de Frontend (`frontend/src/features/logistics/`)
- **Páginas & Views:**
  - `SuppliersPage.tsx` — Conteiner da página global de fornecedores.
  - `VendorsItemsView.tsx` — Visão integrada de fornecedores e itens no contexto de um casamento.
- **Subcomponentes e Dialogs:**
  - `SuppliersTable.tsx`, `SupplierFormDialog.tsx`, `SupplierDetailDialog.tsx` — Gestão de fornecedores.
  - `ContractDetailDialog.tsx`, `EditContractDialog.tsx` — Detalhes e edição de contrato.
  - `ContractUploadDialog.tsx` — Modal avançado de upload de contrato PDF para Cloudflare R2 com geração de despesas e itens. Veja [contract-pdf-upload-r2-flow](../architecture/contract-pdf-upload-r2-flow.md).
  - `ItemsTable.tsx`, `CreateItemDialog.tsx`, `EditItemDialog.tsx` — Gestão de itens contratados.
- **Hooks Customizados:** `useSuppliersPage.ts`, `useContractUpload.ts`, `useContractUploadForm.ts`, `useVendorsItems.ts`.

---

## Regras de Negócio Associadas
- [cnpj-validation-rules](../business-rules/logistics/cnpj-validation-rules.md): Validação de CNPJ de fornecedores no backend e frontend.
- [contract-parent-child-hierarchy](../business-rules/logistics/contract-parent-child-hierarchy.md): Regras de aditivos contratuais e travas no grafo de contratos.
- [contract-state-machine](../business-rules/logistics/contract-state-machine.md): Máquinas de estado e transições permitidas para contratos e itens.
- [contract-pdf-upload-r2-flow](../architecture/contract-pdf-upload-r2-flow.md): Fluxo de upload de contratos em PDF via Cloudflare R2.
