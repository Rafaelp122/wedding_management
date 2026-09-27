import { z } from "zod";
import { SuppliersCreateBody } from "@/api/generated/v1/zod/suppliers/suppliers";

const cnpjRegExp = /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/;

export const SupplierFormSchema = SuppliersCreateBody.extend({
  cnpj: z
    .string()
    .regex(cnpjRegExp, "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX."),
});

export type SupplierFormData = z.infer<typeof SupplierFormSchema>;
