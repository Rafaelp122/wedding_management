# How-To: Padrão de Criação de Formulários com React Hook Form & Zod

> **Objetivo:** Implementar formulários validados no cliente utilizando Schemas Zod gerados pelo Orval e o `react-hook-form`.

---

## Estrutura Recomendada

No projeto, reaproveitamos os schemas de validação Zod gerados automaticamente pelo Orval em `@/api/generated/v1/zod/` e os estendemos (`.extend(...)`) para incluir validações visuais ou customizadas do frontend (ex: Regex de CNPJ, confirmação de senhas, limites).

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
// Importar schema base gerado pelo Orval
import { logisticsSuppliersCreateBody } from "@/api/generated/v1/zod/logisticsSuppliersCreateBody";

// Estender o schema do Orval com validações adicionais do cliente
export const supplierFormSchema = logisticsSuppliersCreateBody.extend({
  cnpj: z
    .string()
    .min(1, "CNPJ é obrigatório")
    .regex(/^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/, "CNPJ deve estar no formato 00.000.000/0000-00"),
});

export type SupplierFormValues = z.infer<typeof supplierFormSchema>;

export function SupplierForm({ onSubmit }: { onSubmit: (data: SupplierFormValues) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<SupplierFormValues>({
    resolver: zodResolver(supplierFormSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("name")} />
      {errors.name && <span>{errors.name.message}</span>}
      <button type="submit">Salvar</button>
    </form>
  );
}
```
