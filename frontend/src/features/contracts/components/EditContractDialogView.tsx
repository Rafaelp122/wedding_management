import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import { ContractsUpdateBody } from "@/api/generated/v1/zod/contracts/contracts";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormSelect, FormSelectNullable, FormNumber, FormTextarea } from "@/components/form-fields";

export type EditContractFormData = z.input<typeof ContractsUpdateBody>;

interface StatusOption {
  value: string;
  label: string;
}

export interface EditContractDialogViewProps {
  contract: ContractOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: EditContractFormData) => void;
  isPending: boolean;
  suppliers: SupplierOut[];
  existingContracts: ContractOut[];
  availableStatusOptions: StatusOption[];
}

export const EditContractDialogView = memo(function EditContractDialogView({
  contract,
  open,
  onOpenChange,
  onSubmit,
  isPending,
  suppliers,
  existingContracts,
  availableStatusOptions,
}: EditContractDialogViewProps) {
  const form = useForm<EditContractFormData>({
    resolver: zodResolver(ContractsUpdateBody),
    defaultValues: {
      supplier: contract.supplier,
      name: contract.name || "",
      total_amount: Number(contract.total_amount),
      status: contract.status,
      description: contract.description || "",
      parent: contract.parent || null,
    },
  });

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Editar Contrato"
      description="Altere os metadados do contrato de fornecedor."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Salvar"
      maxWidth="520px"
    >
      <FormSelect
        control={form.control}
        name="supplier"
        label="Fornecedor"
        items={suppliers}
        getItemKey={(s) => s.uuid}
        getItemLabel={(s) => s.name}
        placeholder="Selecione um fornecedor"
      />

      <FormInput
        control={form.control}
        name="name"
        label="Nome do Contrato"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição"
      />

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="total_amount"
          label="Valor Total"
        />

        <FormSelect
          control={form.control}
          name="status"
          label="Status"
          items={availableStatusOptions}
          getItemKey={(opt) => opt.value}
          getItemLabel={(opt) => opt.label}
        />
      </div>

      {existingContracts.length > 0 && (
        <FormSelectNullable
          control={form.control}
          name="parent"
          label="Contrato Original — Aditivo (Opcional)"
          items={existingContracts}
          getItemKey={(c) => c.uuid}
          getItemLabel={(c) =>
            c.name || c.description || c.uuid.substring(0, 8)
          }
          placeholder="Nenhum (contrato novo)"
          noneLabel="Nenhum (contrato novo)"
        />
      )}
    </FormDialog>
  );
});
