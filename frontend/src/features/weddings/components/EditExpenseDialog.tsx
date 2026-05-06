import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";

import { useFinancesExpensesUpdate } from "@/api/generated/v1/endpoints/finances/finances";
import { useLogisticsContractsList } from "@/api/generated/v1/endpoints/logistics/logistics";
import { FinancesExpensesUpdateBody } from "@/api/generated/v1/zod/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";

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
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { selectOnFocus } from "@/features/shared/utils/selectOnFocus";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

type EditExpenseFormData = z.infer<typeof FinancesExpensesUpdateBody>;

interface EditExpenseDialogProps {
  expense: ExpenseOut;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function EditExpenseDialog({
  expense,
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: EditExpenseDialogProps) {
  const { mutate, isPending } = useFinancesExpensesUpdate();

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items || [];

  const hasPaid = (expense.paid_installments_count ?? 0) > 0;

  const form = useForm<EditExpenseFormData>({
    resolver: zodResolver(FinancesExpensesUpdateBody),
    defaultValues: {
      name: expense.name || "",
      description: expense.description || null,
      estimated_amount: Number(expense.estimated_amount) || 0,
      actual_amount: Number(expense.actual_amount) || 0,
      contract: expense.contract || null,
      num_installments: null,
      first_due_date: null,
    },
  });

  const onSubmit = (data: EditExpenseFormData) => {
    mutate(
      { uuid: expense.uuid, data },
      {
        onSuccess: () => {
          toast.success("Despesa atualizada com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao atualizar despesa.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[560px]">
        <DialogHeader>
          <DialogTitle>Editar Despesa</DialogTitle>
          <DialogDescription>
            Altere os dados da despesa. A categoria não pode ser alterada.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome da Despesa</FormLabel>
                  <FormControl>
                    <Input {...field} value={field.value ?? ""} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

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
                          {contract.description ||
                            contract.uuid.substring(0, 8)}
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
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição (Opcional)</FormLabel>
                  <FormControl>
                    <Textarea
                      {...field}
                      value={field.value ?? ""}
                      rows={2}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="estimated_amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valor Estimado</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        disabled={hasPaid}
                        value={field.value ?? ""}
                        onBlur={field.onBlur}
                        name={field.name}
                        ref={field.ref}
                        onFocus={selectOnFocus}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value === ""
                              ? 0
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
                name="actual_amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valor Realizado</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        disabled={hasPaid}
                        value={field.value ?? ""}
                        onBlur={field.onBlur}
                        name={field.name}
                        ref={field.ref}
                        onFocus={selectOnFocus}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value === ""
                              ? 0
                              : Number(e.target.value),
                          )
                        }
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="num_installments"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nº de Parcelas</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        disabled={hasPaid}
                        placeholder="Manter atual"
                        value={field.value ?? ""}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value === ""
                              ? null
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
                name="first_due_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Venc. 1ª Parcela</FormLabel>
                    <FormControl>
                      <Input
                        type="date"
                        disabled={hasPaid}
                        value={field.value ?? ""}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value === "" ? null : e.target.value,
                          )
                        }
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {hasPaid ? (
              <p className="text-xs text-muted-foreground">
                Valores e parcelamento bloqueados — há parcelas marcadas como
                pagas. Crie uma nova despesa se precisar alterar valores.
              </p>
            ) : null}

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
                {isPending ? <Loader2 className="mr-2 size-4 animate-spin" /> : null}
                Salvar Alterações
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
