import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";

import {
  useLogisticsContractsUpdate,
  useLogisticsContractsList,
  useLogisticsSuppliersList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { LogisticsContractsUpdateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { ContractPatchIn } from "@/api/generated/v1/models/contractPatchIn";
import { SELECT_NONE_VALUE } from "@/features/shared/utils/constants";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
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
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

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
    const payload: ContractPatchIn = {};
    if (data.supplier !== contract.supplier) payload.supplier = data.supplier;
    if (data.name !== (contract.name || "")) payload.name = data.name;
    if (data.total_amount !== Number(contract.total_amount))
      payload.total_amount = data.total_amount;
    if (data.status !== contract.status) payload.status = data.status;
    if (data.description !== (contract.description || ""))
      payload.description = data.description;
    if (data.parent !== contract.parent) payload.parent = data.parent;

    if (Object.keys(payload).length === 0) {
      onOpenChange(false);
      return;
    }

    mutate(
      { uuid: contract.uuid, data: payload as ContractPatchIn },
      {
        onSuccess: () => {
          toast.success("Contrato atualizado com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao atualizar contrato.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[520px]">
        <DialogHeader>
          <DialogTitle>Editar Contrato</DialogTitle>
          <DialogDescription>
            Altere os metadados do contrato de fornecedor.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="supplier"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Fornecedor</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value ?? undefined}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione um fornecedor" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {suppliers.map((s) => (
                        <SelectItem key={s.uuid} value={s.uuid}>
                          {s.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome do Contrato</FormLabel>
                  <FormControl>
                    <Input {...field} value={field.value ?? ""} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição</FormLabel>
                  <FormControl>
                    <Textarea {...field} value={field.value ?? ""} rows={2} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="total_amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valor Total</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder="0.00"
                        value={field.value ?? ""}
                        onBlur={field.onBlur}
                        name={field.name}
                        ref={field.ref}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value === ""
                              ? undefined
                              : Number(e.target.value),
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
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value ?? undefined}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="DRAFT">Rascunho</SelectItem>
                        <SelectItem value="PENDING">Pendente</SelectItem>
                        <SelectItem value="SIGNED">Assinado</SelectItem>
                        <SelectItem value="CANCELED">Cancelado</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {existingContracts.length > 0 && (
              <FormField
                control={form.control}
                name="parent"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Contrato Original — Aditivo (Opcional)</FormLabel>
                    <Select
                      onValueChange={(v) =>
                        field.onChange(v === SELECT_NONE_VALUE ? null : v)
                      }
                      value={field.value ?? SELECT_NONE_VALUE}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Nenhum (contrato novo)" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={SELECT_NONE_VALUE}>
                          Nenhum (contrato novo)
                        </SelectItem>
                        {existingContracts.map((c) => (
                          <SelectItem key={c.uuid} value={c.uuid}>
                            {c.name || c.description || c.uuid.substring(0, 8)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending ? (
                  <Loader2 className="mr-2 size-4 animate-spin" />
                ) : null}
                Salvar
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
});
