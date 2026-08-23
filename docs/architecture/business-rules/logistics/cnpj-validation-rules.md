---
title: "Validação e Sanitização de CNPJ"
domain: logistics
type: business-rule
code: backend/apps/logistics/services/supplier_service.py
tests: backend/apps/logistics/tests/services/test_supplier_service.py
---

# Regra de Negócio: Validação de CNPJ de Fornecedores

> **Módulo:** [logistics-domain](../../domains/logistics-domain.md) | [supplier-model](../../../reference/models/logistics/supplier-model.md)
> **Código:** `backend/apps/logistics/models/supplier.py` (`cnpj_validator`), `frontend/src/features/logistics/hooks/supplierFormSchema.ts`

---

## 1. Validação no Backend (`cnpj_validator`)

No modelo `Supplier`, o campo `cnpj` utiliza o validador customizado `cnpj_validator`:

- **Formato Aceito:** `XX.XXX.XXX/XXXX-XX` (18 caracteres).
- **Validação de Formato e Máscara:** Aplica a verificação de formato e estrutura de 18 caracteres (`XX.XXX.XXX/XXXX-XX`).
- **Unicidade por Tenant:** O CNPJ é único por empresa (`unique_together = [["company", "cnpj"]]`).

---

## 2. Validação no Frontend (`SupplierFormSchema`)

No frontend React, o formulário utiliza o `SupplierFormSchema` (`supplierFormSchema.ts`), que estende a validação gerada pelo Orval via `LogisticsSuppliersCreateBody.extend(...)`:

```typescript
export const SupplierFormSchema = LogisticsSuppliersCreateBody.extend({
  cnpj: z
    .string()
    .regex(/^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/, "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX."),
});
```

Garante o feedback visual imediato antes da submissão para a API.
