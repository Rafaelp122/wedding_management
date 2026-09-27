import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQueryClient } from "@tanstack/react-query";

import type { PlannerContractOut } from "@/api/generated/v1/models/plannerContractOut";
import { PlannerContractServiceTierEnum } from "@/api/generated/v1/models/plannerContractServiceTierEnum";
import { PlannerContractStatusEnum } from "@/api/generated/v1/models/plannerContractStatusEnum";
import {
  useSavePlannerContract,
  getWeddingsReadQueryKey,
  getWeddingsListQueryKey,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import { getDashboardWeddingQueryKey } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import { FormDialog } from "@/components/form-dialog";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const plannerContractSchema = z.object({
  service_tier: z.enum(
    [
      PlannerContractServiceTierEnum.COMPLETA,
      PlannerContractServiceTierEnum.PARCIAL,
      PlannerContractServiceTierEnum.FINAL,
    ],
    { message: "Selecione o nível de serviço" },
  ),
  effective_amount: z
    .number()
    .min(0.01, "O valor dos honorários deve ser maior que zero"),
  installments_count: z
    .number()
    .int("Quantidade de parcelas deve ser inteira")
    .min(1, "Mínimo de 1 parcela"),
  signed_date: z.string().optional().nullable(),
  status: z.enum(
    [
      PlannerContractStatusEnum.DRAFT,
      PlannerContractStatusEnum.SIGNED,
      PlannerContractStatusEnum.CANCELED,
    ],
    { message: "Selecione o status do contrato" },
  ),
});

type PlannerContractFormData = z.infer<typeof plannerContractSchema>;

interface PlannerContractDialogProps {
  weddingUuid: string;
  contract?: PlannerContractOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

/**
 * Componente Smart para cadastro e edição do contrato de honorários da assessoria.
 */
export function PlannerContractDialog({
  weddingUuid,
  contract,
  open,
  onOpenChange,
  onSuccess,
}: PlannerContractDialogProps) {
  const queryClient = useQueryClient();
  const { mutate, isPending } = useSavePlannerContract();

  const form = useForm<PlannerContractFormData>({
    resolver: zodResolver(plannerContractSchema),
    defaultValues: {
      service_tier: (contract?.service_tier as PlannerContractServiceTierEnum) ?? PlannerContractServiceTierEnum.COMPLETA,
      effective_amount: contract?.effective_amount ? Number.parseFloat(contract.effective_amount) : 0,
      installments_count: contract?.installments_count ?? 1,
      signed_date: contract?.signed_date ?? "",
      status: (contract?.status as PlannerContractStatusEnum) ?? PlannerContractStatusEnum.DRAFT,
    },
  });

  useEffect(() => {
    if (open) {
      form.reset({
        service_tier:
          (contract?.service_tier as PlannerContractServiceTierEnum) ??
          PlannerContractServiceTierEnum.COMPLETA,
        effective_amount: contract?.effective_amount
          ? Number.parseFloat(contract.effective_amount)
          : 0,
        installments_count: contract?.installments_count ?? 1,
        signed_date: contract?.signed_date ?? "",
        status:
          (contract?.status as PlannerContractStatusEnum) ??
          PlannerContractStatusEnum.DRAFT,
      });
    }
  }, [open, contract, form]);

  const onSubmit = (values: PlannerContractFormData) => {
    mutate(
      {
        uuid: weddingUuid,
        data: {
          service_tier: values.service_tier,
          effective_amount: values.effective_amount,
          installments_count: values.installments_count,
          signed_date: values.signed_date ? values.signed_date : null,
          status: values.status,
        },
      },
      createMutationCallbacks({
        successMsg: "Contrato de assessoria salvo com sucesso!",
        fallbackErrorMsg: "Erro ao salvar contrato de assessoria.",
        onSuccess: () => {
          queryClient.invalidateQueries({
            queryKey: getWeddingsReadQueryKey(weddingUuid),
          });
          queryClient.invalidateQueries({
            queryKey: getWeddingsListQueryKey(),
          });
          queryClient.invalidateQueries({
            queryKey: getDashboardWeddingQueryKey(weddingUuid),
          });
          onOpenChange(false);
          onSuccess?.();
        },
      }),
    );
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={contract ? "Editar Contrato de Assessoria" : "Contrato de Assessoria"}
      description="Informe os honorários e escopo da contratação da assessoria para este casamento."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Salvar Contrato"
      maxWidth="520px"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="service_tier"
          render={({ field }) => (
            <FormItem className="sm:col-span-2">
              <FormLabel>Nível de Serviço</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger aria-label="Nível de Serviço">
                    <SelectValue placeholder="Selecione o nível" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value={PlannerContractServiceTierEnum.COMPLETA}>
                    Assessoria Completa
                  </SelectItem>
                  <SelectItem value={PlannerContractServiceTierEnum.PARCIAL}>
                    Assessoria Parcial
                  </SelectItem>
                  <SelectItem value={PlannerContractServiceTierEnum.FINAL}>
                    Assessoria Final / Cerimonial
                  </SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="effective_amount"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Valor dos Honorários (R$)</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Ex: 5000.00"
                  value={field.value || ""}
                  onChange={(e) =>
                    field.onChange(
                      e.target.value === "" ? 0 : Number.parseFloat(e.target.value),
                    )
                  }
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="installments_count"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Número de Parcelas</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  min="1"
                  placeholder="Ex: 3"
                  value={field.value || ""}
                  onChange={(e) =>
                    field.onChange(
                      e.target.value === "" ? 1 : Number.parseInt(e.target.value, 10),
                    )
                  }
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="signed_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Data de Assinatura</FormLabel>
              <FormControl>
                <Input
                  type="date"
                  value={field.value ?? ""}
                  onChange={(e) => field.onChange(e.target.value || null)}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="status"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status do Contrato</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger aria-label="Status do Contrato">
                    <SelectValue placeholder="Selecione o status" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value={PlannerContractStatusEnum.DRAFT}>
                    Rascunho
                  </SelectItem>
                  <SelectItem value={PlannerContractStatusEnum.SIGNED}>
                    Assinado
                  </SelectItem>
                  <SelectItem value={PlannerContractStatusEnum.CANCELED}>
                    Cancelado
                  </SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </FormDialog>
  );
}
