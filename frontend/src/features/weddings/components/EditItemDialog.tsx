import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";

import {
  useLogisticsItemsUpdate,
  useLogisticsContractsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { LogisticsItemsUpdateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";

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

type EditItemFormData = z.infer<typeof LogisticsItemsUpdateBody>;

interface EditItemDialogProps {
  item: ItemOut;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const EditItemDialog = memo(function EditItemDialog({
  item,
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: EditItemDialogProps) {
  const { mutate, isPending } = useLogisticsItemsUpdate();

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items ?? [];

  const form = useForm<EditItemFormData>({
    resolver: zodResolver(LogisticsItemsUpdateBody),
    defaultValues: {
      name: item.name,
      description: item.description || "",
      quantity: item.quantity,
      contract: item.contract ?? null,
      acquisition_status: item.acquisition_status,
    },
  });

  const onSubmit = (data: EditItemFormData) => {
    const payload: Record<string, unknown> = {};
    if (data.name !== item.name) payload.name = data.name;
    if (data.description !== (item.description || ""))
      payload.description = data.description;
    if (data.quantity !== item.quantity) payload.quantity = data.quantity;
    if (data.contract !== item.contract) payload.contract = data.contract;
    if (data.acquisition_status !== item.acquisition_status)
      payload.acquisition_status = data.acquisition_status;

    if (Object.keys(payload).length === 0) {
      onOpenChange(false);
      return;
    }

    mutate(
      { uuid: item.uuid, data: payload as EditItemFormData },
      {
        onSuccess: () => {
          toast.success("Item atualizado com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao atualizar item.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Editar Item</DialogTitle>
          <DialogDescription>
            Altere as informações do item logístico.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome</FormLabel>
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
                name="quantity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Quantidade</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        {...field}
                        value={field.value ?? ""}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value === ""
                              ? 1
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
                name="acquisition_status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value ?? undefined}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Status" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="PENDING">Pendente</SelectItem>
                        <SelectItem value="IN_PROGRESS">Em Andamento</SelectItem>
                        <SelectItem value="DONE">Concluído</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="contract"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Contrato (Opcional)</FormLabel>
                  <Select
                    onValueChange={(v) =>
                      field.onChange(v === "__none__" ? null : v)
                    }
                    value={field.value ?? "__none__"}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Nenhum contrato" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="__none__">Nenhum</SelectItem>
                      {contracts.map((contract) => (
                        <SelectItem key={contract.uuid} value={contract.uuid}>
                          {contract.supplier_name ||
                            contract.description ||
                            contract.uuid.substring(0, 8)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

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
