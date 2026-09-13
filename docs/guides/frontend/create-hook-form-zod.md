# Como Criar Formulários com React Hook Form & Zod

> **Categoria:** [frontend](../../reference/frontend/index.md) | [generate-orval-client](generate-orval-client.md) | [ui-components-spec](../../reference/frontend/ui-components-spec.md)
> **Stack:** React 19, `react-hook-form`, `@hookform/resolvers/zod`, `zod`, `shadcn/ui`, `sonner`

---

## Visão Geral

No **Wedding Management System (WMS)**, a construção de formulários segue uma arquitetura baseada em tipagem estrita de ponta a ponta:
1. **Reaproveitamento de Schemas Zod:** Os schemas base gerados automaticamente pelo Orval em `@/api/generated/v1/zod/` são estendidos (`.extend(...)`) para adicionar regras de negócio do cliente (mensagens amigáveis em PT-BR, regex de CNPJ/CPF, etc.).
2. **Gerenciamento de Estado:** O `react-hook-form` com `zodResolver` gerencia as validações síncronas sem causar re-renderizações desnecessárias na árvore de componentes.
3. **Componentes Visuais:** A UI é composta com os blocos acessíveis do **shadcn/ui** (`Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage`).

---

## Passo 1: Definir e Estender o Schema de Validação Zod

Importe o schema base gerado pelo Orval e estenda suas propriedades para enriquecer com validações locais:

```typescript
// src/features/logistics/schemas/supplierFormSchema.ts
import { z } from "zod";
import { logisticsSuppliersCreateBody } from "@/api/generated/v1/zod/logisticsSuppliersCreateBody";

export const supplierFormSchema = logisticsSuppliersCreateBody.extend({
  name: z
    .string()
    .min(3, "O nome do fornecedor deve ter no mínimo 3 caracteres.")
    .max(150, "O nome não pode exceder 150 caracteres."),
  cnpj: z
    .string()
    .min(1, "CNPJ é obrigatório.")
    .regex(
      /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/,
      "CNPJ inválido. Utilize o formato 00.000.000/0000-00."
    ),
  category: z.string().min(1, "Selecione uma categoria de fornecedor."),
  email: z.string().email("Informe um e-mail válido.").optional().or(z.literal("")),
  phone: z.string().max(20, "Telefone inválido.").optional().or(z.literal("")),
});

export type SupplierFormValues = z.infer<typeof supplierFormSchema>;
```

---

## Passo 2: Construir o Componente de Formulário com shadcn/ui

Crie o componente de formulário utilizando os wrappers tipados do shadcn/ui:

```tsx
// src/features/logistics/components/SupplierForm.tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  supplierFormSchema,
  type SupplierFormValues,
} from "../schemas/supplierFormSchema";

interface SupplierFormProps {
  initialValues?: Partial<SupplierFormValues>;
  onSubmit: (data: SupplierFormValues) => void;
  isSubmitting?: boolean;
}

export function SupplierForm({
  initialValues,
  onSubmit,
  isSubmitting = false,
}: SupplierFormProps) {
  const form = useForm<SupplierFormValues>({
    resolver: zodResolver(supplierFormSchema),
    defaultValues: {
      name: initialValues?.name ?? "",
      cnpj: initialValues?.cnpj ?? "",
      category: initialValues?.category ?? "",
      email: initialValues?.email ?? "",
      phone: initialValues?.phone ?? "",
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Campo: Nome do Fornecedor */}
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nome do Fornecedor *</FormLabel>
              <FormControl>
                <Input placeholder="Ex: Buffet Real & Gastronomia" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Campo: CNPJ com Formatação */}
        <FormField
          control={form.control}
          name="cnpj"
          render={({ field }) => (
            <FormItem>
              <FormLabel>CNPJ *</FormLabel>
              <FormControl>
                <Input placeholder="00.000.000/0000-00" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Campo: Categoria */}
        <FormField
          control={form.control}
          name="category"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Categoria *</FormLabel>
              <FormControl>
                <Input placeholder="Ex: Gastronomia, Fotografia, Decoração" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Botão de Submissão com Estado de Loading */}
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Salvando..." : "Salvar Fornecedor"}
        </Button>
      </form>
    </Form>
  );
}
```

---

## Passo 3: Integrar o Formulário com Mutações do Orval

No componente container (*Smart Component*), conecte o formulário à mutação gerada pelo Orval e forneça feedback visual com `sonner`:

```tsx
// src/features/logistics/components/CreateSupplierDialog.tsx
import { useLogisticsSuppliersCreate } from "@/api/generated/v1/endpoints/logistics/logistics";
import { toast } from "sonner";
import { SupplierForm } from "./SupplierForm";
import type { SupplierFormValues } from "../schemas/supplierFormSchema";

export function CreateSupplierDialog({ onSuccess }: { onSuccess: () => void }) {
  const { mutate, isPending } = useLogisticsSuppliersCreate();

  const handleSubmit = (data: SupplierFormValues) => {
    mutate(
      { data },
      {
        onSuccess: () => {
          toast.success("Fornecedor cadastrado com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const apiMessage = error.response?.data?.message ?? "Falha ao cadastrar fornecedor.";
          toast.error(apiMessage);
        },
      }
    );
  };

  return <SupplierForm onSubmit={handleSubmit} isSubmitting={isPending} />;
}
```

---

## Regras de Ouro de Formulários no WMS

> [!IMPORTANT]
> **1. Sempre Forneça `defaultValues`:**
> O React emitirá alertas caso um input mude de não controlado para controlado. Sempre defina strings vazias `""` ou números `0` no `defaultValues` do `useForm`.

> [!TIP]
> **2. Desabilite Múltiplos Submits:**
> Sempre repasse o estado `isPending` / `isSubmitting` da mutação para o botão de envio, prevenindo submissões duplicadas no backend.

---

## Troubleshooting & Resolução de Problemas

### 1. Submit Clicado sem Reação Visual ou Envio
- **Sintoma:** Clicar no botão de submit não dispara a mutação e nenhum erro vermelho aparece na tela.
- **Causa:** Um campo oculto no formulário ou não renderizado no DOM falhou na validação do Zod.
- **Solução:** Inspecione os erros do formulário adicionando um callback de erro no `handleSubmit`:
  ```tsx
  <form onSubmit={form.handleSubmit(onSubmit, (errors) => console.error("Erros de Validação:", errors))}>
  ```

### 2. Discrepância de Tipos entre `z.infer` e API Payload
- **Sintoma:** TypeScript aponta erro de tipo ao passar `data` para o `mutate({ data })`.
- **Solução:** Se você aplicou `.transform()` no schema Zod, utilize `z.input<typeof schema>` para o formulário e `z.output<typeof schema>` para o payload enviado à mutação.
