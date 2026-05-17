import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import {
  useLogisticsContractsUpdate,
  useLogisticsContractsList,
  useLogisticsSuppliersList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { LogisticsContractsUpdateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { ContractPatchIn } from "@/api/generated/v1/models/contractPatchIn";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormSelect, FormSelectNullable, FormNumber, FormTextarea } from "@/components/form-fields";
import { CONTRACT_STATUS_OPTIONS } from "@/features/logistics/constants";
import { buildPatchPayload } from "@/lib/patch-payload";

type EditContractFormData = z.infer<typeof LogisticsContractsUpdateBody>;

interface EditContractDialogProps {
  contract: ContractOut;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const EditContractDialog = memo(function EditContractDialog({
  contract,
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: EditContractDialogProps) {
  const { mutate, isPending } = useLogisticsContractsUpdate();

  const { data: suppliersResponse } = useLogisticsSuppliersList();
  const suppliers = suppliersResponse?.data?.items ?? [];

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const existingContracts =
    contractsResponse?.data?.items?.filter((c) => c.uuid !== contract.uuid) ?? [];

  const form = useForm<EditContractFormData>({
    resolver: zodResolver(LogisticsContractsUpdateBody),
    defaultValues: {
      supplier: contract.supplier,
      name: contract.name || "",
      total_amount: Number(contract.total_amount),
      status: contract.status,
      description: contract.description || "",
      parent: contract.parent || null,
    },
  });

  const onSubmit = (data: EditContractFormData) => {
    const original: Record<string, unknown> = {
      supplier: contract.supplier,
      name: contract.name || "",
      total_amount: Number(contract.total_amount),
      status: contract.status,
      description: contract.description || "",
      parent: contract.parent ?? null,
    };
    const modified: Record<string, unknown> = {
      supplier: data.supplier,
      name: data.name,
      total_amount: data.total_amount,
      status: data.status,
      description: data.description,
      parent: data.parent ?? null,
    };

    const payload = buildPatchPayload(original, modified, [
      "supplier",
      "name",
      "total_amount",
      "status",
      "description",
      "parent",
    ]);

    if (Object.keys(payload).length === 0) {
      onOpenChange(false);
      return;
    }

    mutate(
      { uuid: contract.uuid, data: payload as ContractPatchIn },
      createMutationCallbacks({
        successMsg: "Contrato atualizado com sucesso!",
        fallbackErrorMsg: "Erro ao atualizar contrato.",
        onSuccess: () => onSuccess(),
      }),
    );
  };

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
          items={CONTRACT_STATUS_OPTIONS}
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
