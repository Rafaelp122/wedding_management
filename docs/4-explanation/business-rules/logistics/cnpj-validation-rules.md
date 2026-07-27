# Regra de Negócio: Validação de CNPJ de Fornecedores

> **Módulo:** [logistics-domain](../../domains/logistics-domain.md) | [supplier-model](../../../3-reference/models/logistics/supplier-model.md)
> **Código:** `backend/apps/logistics/models/supplier.py` (`cnpj_validator`), `frontend/src/features/logistics/hooks/supplierFormSchema.ts`

---

## 1. Validação no Backend (`cnpj_validator`)

No modelo `Supplier`, o campo `cnpj` utiliza o validador customizado `cnpj_validator`:

- **Formato Aceito:** `XX.XXX.XXX/XXXX-XX` (18 caracteres).
- **Algoritmo de Verificação:** Executa a checagem oficial dos 14 dígitos numéricos e valida o cálculo dos dois dígitos verificadores (DV1 e DV2).
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
