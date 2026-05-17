import { memo } from "react";
import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import {
  useLogisticsItemsCreate,
  useLogisticsContractsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { LogisticsItemsCreateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormSelect, FormSelectNullable, FormNumber, FormTextarea } from "@/components/form-fields";
import { ACQUISITION_STATUS_OPTIONS } from "@/features/logistics/constants";

type CreateItemFormData = z.infer<typeof LogisticsItemsCreateBody>;

interface CreateItemDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const CreateItemDialog = memo(function CreateItemDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: CreateItemDialogProps) {
  const { mutate, isPending } = useLogisticsItemsCreate();

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items ?? [];

  const form = useForm<CreateItemFormData>({
    resolver: zodResolver(LogisticsItemsCreateBody) as Resolver<CreateItemFormData>,
    defaultValues: {
      wedding: weddingUuid,
      contract: null,
      name: "",
      description: "",
      quantity: 1,
      acquisition_status: "PENDING",
    },
  });

  const onSubmit = (data: CreateItemFormData) => {
    mutate(
      { data },
      createMutationCallbacks({
        successMsg: "Item criado com sucesso!",
        fallbackErrorMsg: "Erro ao criar item.",
        onSuccess: () => {
          form.reset();
          onSuccess();
        },
      }),
    );
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Novo Item"
      description="Registre um item logístico vinculado ao evento."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Item"
      maxWidth="480px"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome"
        placeholder="Ex: Buquê de rosas"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição (Opcional)"
        placeholder="Detalhes do item..."
      />

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="quantity"
          label="Quantidade"
          step="1"
          min={1}
          transformEmptyTo={1}
        />

        <FormSelect
          control={form.control}
          name="acquisition_status"
          label="Status"
          items={ACQUISITION_STATUS_OPTIONS}
          getItemKey={(opt) => opt.value}
          getItemLabel={(opt) => opt.label}
          placeholder="Status"
        />
      </div>

      <FormSelectNullable
        control={form.control}
        name="contract"
        label="Contrato (Opcional)"
        items={contracts}
        getItemKey={(c) => c.uuid}
        getItemLabel={(c) =>
          c.supplier_name || c.description || c.uuid.substring(0, 8)
        }
        placeholder="Nenhum contrato"
      />
    </FormDialog>
  );
});
