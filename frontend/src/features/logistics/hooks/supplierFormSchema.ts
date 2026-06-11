import * as zod from "zod";
import { LogisticsSuppliersCreateBody } from "@/api/generated/v1/zod/logistics/logistics";

const cnpjRegExp = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/;

export const SupplierFormSchema = LogisticsSuppliersCreateBody.extend({
  cnpj: zod
    .string()
    .regex(cnpjRegExp, "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX."),
});

export type SupplierFormData = zod.infer<typeof SupplierFormSchema>;
